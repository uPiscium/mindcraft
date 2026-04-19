from __future__ import annotations

# ruff: noqa: E402, I001

from pathlib import Path

import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from mindcraft_py.runtime import MindcraftRuntime


def main() -> None:
    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(repo_root / "tasks" / "task_pool_demo.toml")

    ordered = runtime.get_ready_task_order()
    print("BFS task order:")
    for task_id in ordered:
        task = runtime.acquire_task_by_id("Andy", task_id)
        print(f"acquired: {task['id']} -> {task['payload']}")
        completed = runtime.complete_task("Andy", task_id, "demo completed")
        print(f"completed: {completed['task']['id']} ({completed['task']['state']})")


if __name__ == "__main__":
    main()
