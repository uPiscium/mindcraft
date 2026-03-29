from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class NodeRuntimeProcess:
    def __init__(self, repo_root=None, node_binary=None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
        self.node_binary = node_binary or shutil.which("node")
        self.process = None

    def build_command(self, profiles=None, task_path=None, task_id=None):
        if self.node_binary is None:
            raise RuntimeError(
                "Node.js is required to launch the current Mindcraft runtime."
            )

        command = [self.node_binary, str(self.repo_root / "main.js")]
        if profiles:
            command.extend(["--profiles", *profiles])
        if task_path:
            command.extend(["--task_path", task_path])
        if task_id:
            command.extend(["--task_id", task_id])
        return command

    def start(self, profiles=None, task_path=None, task_id=None):
        command = self.build_command(profiles, task_path, task_id)
        self.process = subprocess.Popen(
            command,
            cwd=self.repo_root,
            env=os.environ.copy(),
        )
        return self.process

    def wait(self):
        if self.process is None:
            return 0
        return self.process.wait()

    def stop(self, timeout=10):
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=timeout)

    def restart(self, profiles=None, task_path=None, task_id=None, timeout=10):
        self.stop(timeout=timeout)
        return self.start(profiles=profiles, task_path=task_path, task_id=task_id)
