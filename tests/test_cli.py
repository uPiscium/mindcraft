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
        task_pool_file=None,
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
