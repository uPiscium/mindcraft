from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
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

    result = subprocess.run(command, cwd=repo_root, env=os.environ.copy())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
