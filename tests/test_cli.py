from argparse import Namespace
from pathlib import Path

from mindcraft_py.cli import build_command
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
