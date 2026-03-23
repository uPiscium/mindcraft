import sys
from datetime import datetime
from io import StringIO

from mindcraft_py.terminal_logging import TerminalLogCapture, resolve_log_path


def test_resolve_log_path_uses_expected_layout(tmp_path):
    fixed_now = datetime(2026, 3, 23, 14, 5)

    path = resolve_log_path(now=fixed_now, base_dir=tmp_path)

    assert path == tmp_path / "2026-03-23" / "1405.log"
    assert path.parent.exists()


def test_terminal_log_capture_teees_stdout_and_stderr(tmp_path, monkeypatch):
    fake_stdout = StringIO()
    fake_stderr = StringIO()
    fake_now = datetime(2026, 3, 23, 14, 5)

    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    with TerminalLogCapture(now=fake_now, base_dir=tmp_path) as log_path:
        print("hello")
        sys.stderr.write("error\n")

    assert log_path == tmp_path / "2026-03-23" / "1405.log"
    content = log_path.read_text(encoding="utf-8")
    assert "hello" in content
    assert "error" in content
    assert "hello" in fake_stdout.getvalue()
    assert "error" in fake_stderr.getvalue()
