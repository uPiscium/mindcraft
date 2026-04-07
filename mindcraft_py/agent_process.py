from __future__ import annotations

import time

from mindcraft_py.node_runtime import NodeRuntimeProcess
from mindcraft_py.python_agent_process import PythonAgentProcess


class AgentProcess(PythonAgentProcess):
    def __init__(self, name, node_runtime=None, logout_agent=None):
        runtime_port = getattr(node_runtime, "port", 0) if node_runtime else 0
        super().__init__(name, runtime_port)
        self.name = name
        self.node_runtime = node_runtime or NodeRuntimeProcess()
        self.logout_agent = logout_agent or (lambda agent_name: None)

    def start(
        self, load_memory=False, init_message=None, count_id=0, profile_path=None
    ):
        process = self.node_runtime.start(
            profiles=[profile_path] if profile_path else None
        )
        super().start(
            load_memory=load_memory,
            init_message=init_message,
            count_id=count_id,
            profile_path=profile_path,
        )
        self.process = process
        return process

    def stop(self):
        self.node_runtime.stop()
        super().stop()

    def handle_exit(self, code=None, signal=None):
        self.logout_agent(self.name)
        if code is not None and code > 1:
            raise SystemExit(code)
        return self.should_restart(code=code, signal=signal)

    def should_restart(self, code=None, signal=None):
        if self._stop_requested or signal == "SIGINT":
            return False
        if code is not None and code > 1:
            return False
        return (time.time() - self.last_restart) >= 10

    def force_restart(self):
        profile_path = None
        if self._start_options:
            profile_path = self._start_options.get("profile_path")
        self.node_runtime.restart(profiles=[profile_path] if profile_path else None)
        return super().force_restart()

    def run(self, profile_path=None, load_memory=False, init_message=None, count_id=0):
        self.start(
            profile_path=profile_path,
            load_memory=load_memory,
            init_message=init_message,
            count_id=count_id,
        )
        return 0
