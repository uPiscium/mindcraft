from __future__ import annotations

import sys
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_ROOT = PROJECT_ROOT / "logs"


def resolve_log_path(
    now: datetime | None = None, base_dir: Path = DEFAULT_LOG_ROOT
) -> Path:
    current_time = now or datetime.now()
    log_dir = base_dir / current_time.strftime("%Y-%m-%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{current_time.strftime('%H%M')}.log"


@dataclass
class _TeeStream:
    original: Any
    log_file: TextIO

    def write(self, text):
        self.original.write(text)
        self.log_file.write(text)
        return len(text)

    def flush(self):
        self.original.flush()
        self.log_file.flush()

    def isatty(self):
        return getattr(self.original, "isatty", lambda: False)()


class TerminalLogCapture(AbstractContextManager[Path]):
    def __init__(self, now: datetime | None = None, base_dir: Path = DEFAULT_LOG_ROOT):
        self.log_path = resolve_log_path(now=now, base_dir=base_dir)
        self._file = None
        self._stdout = None
        self._stderr = None

    def __enter__(self):
        self._file = self.log_path.open("a", encoding="utf-8")
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = _TeeStream(self._stdout, self._file)
        sys.stderr = _TeeStream(self._stderr, self._file)
        return self.log_path

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._file:
                self._file.flush()
        finally:
            if self._stdout is not None:
                sys.stdout = self._stdout
            if self._stderr is not None:
                sys.stderr = self._stderr
            if self._file:
                self._file.close()
        return False


def setup_terminal_logging(
    now: datetime | None = None, base_dir: Path = DEFAULT_LOG_ROOT
):
    return TerminalLogCapture(now=now, base_dir=base_dir)
