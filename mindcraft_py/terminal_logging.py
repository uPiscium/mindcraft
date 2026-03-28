from __future__ import annotations

import sys
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path


def resolve_log_path(now=None, base_dir="logs"):
    now = now or datetime.now()
    base_dir = Path(base_dir)
    log_dir = base_dir / now.strftime("%Y-%m-%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / now.strftime("%H%M.log")


class TerminalLogCapture(AbstractContextManager):
    def __init__(self, now=None, base_dir="logs"):
        self.now = now or datetime.now()
        self.base_dir = base_dir
        self._stdout = None
        self._stderr = None
        self._file = None
        self._log_path = None

    def __enter__(self):
        self._log_path = resolve_log_path(self.now, self.base_dir)
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self._file = self._log_path.open("a", encoding="utf-8")
        sys.stdout = _Tee(self._stdout, self._file)
        sys.stderr = _Tee(self._stderr, self._file)
        return self._log_path

    def __exit__(self, exc_type, exc, tb):
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        if self._file:
            self._file.close()
        return False


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()
