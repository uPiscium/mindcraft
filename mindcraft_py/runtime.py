import atexit
import copy
import os
import socket
import subprocess
import sys
import threading
import time

import socketio
from socketio.exceptions import ConnectionError as SocketIOConnectionError

from .node_runtime import resolve_node_executable


class MindcraftRuntime:
    def __init__(self):
        self.sio = socketio.Client(reconnection=True)
        self.process = None
        self.connected = False
        self.log_thread = None
        self.port = 8080
        self._shutdown_lock = threading.Lock()
        self._shutdown_complete = False

    def _log_reader(self):
        if not self.process or not self.process.stdout:
            return
        for line in iter(self.process.stdout.readline, ""):
            if not line:
                break
            sys.stdout.write(f"[Node.js] {line}")
            sys.stdout.flush()

    def _is_port_open(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                return False

    def _wait_for_port(self, host, port, timeout):
        start = time.time()
        while time.time() - start < timeout:
            if self._is_port_open(host, port):
                return True
            time.sleep(0.2)
        return False

    def init(self, port=8080, host_public=True, auto_open_ui=True, startup_timeout=20):
        if self.process:
            return

        self._shutdown_complete = False
        self.port = port

        node_script_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "src",
                "mindcraft-py",
                "init-mindcraft.js",
            )
        )

        node_executable = resolve_node_executable(os.environ)
        args = [
            node_executable,
            node_script_path,
            "--mindserver_port",
            str(port),
            "--host_public",
            "true" if host_public else "false",
            "--auto_open_ui",
            "true" if auto_open_ui else "false",
        ]

        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self.log_thread = threading.Thread(target=self._log_reader, daemon=True)
        self.log_thread.start()

        atexit.register(self.shutdown)

        if not self._wait_for_port("127.0.0.1", port, startup_timeout):
            self.shutdown()
            raise RuntimeError(
                f"MindServer did not start on port {port} within {startup_timeout}s"
            )

        try:
            self.sio.connect(f"http://localhost:{port}", wait_timeout=startup_timeout)
            self.connected = True
            print(f"Connected to MindServer at localhost:{port}.")
        except SocketIOConnectionError as error:
            self.shutdown()
            raise RuntimeError(f"Failed to connect to MindServer: {error}") from error

    def create_agent(self, settings_json, timeout=60):
        if not self.connected:
            raise RuntimeError("Not connected to MindServer. Call init() first.")

        payload = copy.deepcopy(settings_json)
        result = self._emit_with_callback("create-agent", payload, timeout=timeout)

        if not result.get("success"):
            error = result.get("error", "Unknown error")
            raise RuntimeError(f"Error creating agent: {error}")

        profile_name = payload.get("profile", {}).get("name", "<unknown>")
        print(f"Agent '{profile_name}' created successfully")
        return result

    def execute_query_command(self, agent_name, message, timeout=60):
        result = self._emit_with_callback(
            "run-query-command",
            {"agentName": agent_name, "message": message},
            timeout=timeout,
        )

        if not result.get("success"):
            error = result.get("error", "Unknown error")
            raise RuntimeError(f"Error executing query command: {error}")

        return result.get("result")

    def _emit_with_callback(self, event_name, payload, timeout=60):
        done = threading.Event()
        result = {"success": False, "error": "No response received"}

        def callback(response):
            if isinstance(response, dict):
                result.update(response)
            done.set()

        self.sio.emit(event_name, payload, callback=callback)
        if not done.wait(timeout):
            raise TimeoutError(f"{event_name} callback timed out after {timeout}s")

        return result

    def shutdown(self):
        with self._shutdown_lock:
            if self._shutdown_complete:
                return
            self._shutdown_complete = True

        if self.sio.connected:
            self.sio.disconnect()
        self.connected = False

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
            self.process = None

        print("Mindcraft shut down.")

    def wait(self):
        print("Server is running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
