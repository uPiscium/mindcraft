from __future__ import annotations

import time


class PythonAgentProcess:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.process = None
        self.running = False
        self._stop_requested = False
        self._start_options = None
        self.last_restart = 0

    def start(
        self, load_memory=False, init_message=None, count_id=0, profile_path=None
    ):
        self._start_options = {
            "load_memory": load_memory,
            "init_message": init_message,
            "count_id": count_id,
            "profile_path": profile_path,
        }
        self.running = True
        self._stop_requested = False
        self.last_restart = time.time()
        self.process = object()
        return self.process

    def stop(self):
        if not self.running:
            return
        self._stop_requested = True
        self.running = False

    def force_restart(self):
        self.stop()
        if self._start_options:
            return self.start(**self._start_options)
        return self.start()
