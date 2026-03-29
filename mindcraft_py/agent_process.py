from __future__ import annotations

import time


class AgentProcess:
    def __init__(self, name, node_runtime, logout_agent=None):
        self.name = name
        self.node_runtime = node_runtime
        self.logout_agent = logout_agent or (lambda agent_name: None)
        self.count_id = 0
        self.running = False
        self.process = None
        self.last_restart = 0

    def start(
        self, profile_path=None, load_memory=False, init_message=None, count_id=0
    ):
        self.count_id = count_id
        self.running = True
        self.last_restart = time.time()

        profiles = [profile_path] if profile_path else None
        self.process = self.node_runtime.start(profiles=profiles)
        return self.process

    def stop(self):
        if not self.running:
            return
        self.node_runtime.stop()
        self.running = False

    def handle_exit(self, code=None, signal=None):
        self.running = False
        self.logout_agent(self.name)

        if code is not None and code > 1:
            raise SystemExit(code)

        if code != 0 and signal != "SIGINT":
            if time.time() - self.last_restart < 10:
                return False
            self.last_restart = time.time()
            self.start(count_id=self.count_id)
            return True

        return False

    def force_restart(self):
        if self.running and self.process is not None:
            self.stop()
            if self.process is not None:
                self.start(count_id=self.count_id)
        else:
            self.start(count_id=self.count_id)
