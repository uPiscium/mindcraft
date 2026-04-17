import json
from argparse import Namespace
from pathlib import Path

from mindcraft_py.cli import (
    build_command,
    choose_mindserver_port,
    resolve_mindserver_port,
)
from mindcraft_py.node_runtime import NodeRuntimeProcess


def test_build_command_passes_profiles_and_task_args():
    args = Namespace(
        profiles=["./agents/Andy.toml"],
        task_path="./tasks/basic/single_agent.json",
        task_id="gather_oak_logs",
    )

    command, repo_root = build_command(args, repo_root=Path("/repo"))

    assert repo_root == Path("/repo")
    assert command == [
        "node",
        "/repo/main.js",
        "--profiles",
        "./agents/Andy.toml",
        "--task_path",
        "./tasks/basic/single_agent.json",
        "--task_id",
        "gather_oak_logs",
    ]


def test_node_runtime_build_command_uses_node_binary(tmp_path):
    runtime = NodeRuntimeProcess(repo_root=tmp_path, node_binary="/usr/bin/node")

    command = runtime.build_command(["./agents/Andy.toml"], task_id="gather_oak_logs")

    assert command == [
        "/usr/bin/node",
        str(tmp_path / "main.js"),
        "--profiles",
        "./agents/Andy.toml",
        "--task_id",
        "gather_oak_logs",
    ]


def test_resolve_mindserver_port_prefers_free_port(monkeypatch):
    def fake_is_port_open(host, port):
        return port == 8080

    monkeypatch.setattr("mindcraft_py.cli.is_port_open", fake_is_port_open)

    assert resolve_mindserver_port(8080) == 8081


def test_choose_mindserver_port_keeps_requested_when_free(monkeypatch):
    monkeypatch.setattr("mindcraft_py.cli.is_port_open", lambda host, port: False)

    assert choose_mindserver_port(8080) == 8080


def test_choose_mindserver_port_logs_when_swapping(monkeypatch, capsys):
    def fake_is_port_open(host, port):
        return port == 8080

    monkeypatch.setattr("mindcraft_py.cli.is_port_open", fake_is_port_open)

    assert choose_mindserver_port(8080) == 8081
    captured = capsys.readouterr()
    assert "switching to 8081" in captured.out


def test_main_loads_task_pool_file_into_environment(monkeypatch, tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "gather_oak_logs"
payload = "Collect logs"
""",
        encoding="utf-8",
    )

    monkeypatch.setattr("mindcraft_py.cli.shutil.which", lambda _: "/usr/bin/node")
    monkeypatch.setattr(
        "mindcraft_py.cli.choose_mindserver_port", lambda port, host="127.0.0.1": 8080
    )

    captured = {}

    def fake_run(command, cwd=None, env=None):
        captured["command"] = command
        captured["env"] = env

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr("mindcraft_py.cli.subprocess.run", fake_run)

    from mindcraft_py.cli import main

    exit_code = main(["--task_pool_file", str(task_file)])

    assert exit_code == 0
    assert "TASK_POOL_JSON" in captured["env"]
    payload = json.loads(captured["env"]["TASK_POOL_JSON"])
    assert payload[0]["id"] == "gather_oak_logs"
