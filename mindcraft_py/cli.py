from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import socket
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mindcraft-py",
        description="Launch the Mindcraft agent runtime from Python.",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        help="One or more TOML profile paths to launch.",
    )
    parser.add_argument(
        "--task_path",
        help="Path to a task JSON file to execute.",
    )
    parser.add_argument(
        "--task_id",
        help="Task identifier to run from the task file.",
    )
    return parser


def build_command(args, repo_root=None):
    repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
    command = ["node", str(repo_root / "main.js")]
    if args.profiles:
        command.extend(["--profiles", *args.profiles])
    if args.task_path:
        command.extend(["--task_path", args.task_path])
    if args.task_id:
        command.extend(["--task_id", args.task_id])
    return command, repo_root


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def resolve_mindserver_port(preferred_port, host="127.0.0.1"):
    if preferred_port is None:
        preferred_port = 8080
    preferred_port = int(preferred_port)
    if not is_port_open(host, preferred_port):
        return preferred_port
    for candidate in range(preferred_port + 1, preferred_port + 101):
        if not is_port_open(host, candidate):
            return candidate
    raise RuntimeError(
        f"No free MindServer port found near {preferred_port}; set MINDSERVER_PORT manually."
    )


def choose_mindserver_port(requested_port, host="127.0.0.1"):
    resolved_port = resolve_mindserver_port(requested_port, host=host)
    if requested_port is not None and int(requested_port) != resolved_port:
        print(
            f"MindServer port {requested_port} is in use; switching to {resolved_port}."
        )
    return resolved_port


def log_mindserver_port(port):
    print(f"Using MindServer port {port}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    node_path = shutil.which("node")
    if node_path is None:
        raise RuntimeError(
            "Node.js is required to launch the current Mindcraft runtime."
        )

    command, repo_root = build_command(args)
    command[0] = node_path

    env = os.environ.copy()
    mindserver_port = choose_mindserver_port(
        env.get("MINDSERVER_PORT"), host="127.0.0.1"
    )
    env["MINDSERVER_PORT"] = str(mindserver_port)
    log_mindserver_port(mindserver_port)

    result = subprocess.run(command, cwd=repo_root, env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
