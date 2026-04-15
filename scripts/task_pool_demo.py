from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from mindcraft_py.runtime import MindcraftRuntime


def main() -> None:
    runtime = MindcraftRuntime()

    runtime.register_task({"id": "task-1", "payload": "gather oak logs"})
    runtime.register_task(
        {
            "id": "task-2",
            "payload": "craft planks",
            "depends_on": ["task-1"],
        }
    )

    print("Initial tasks:")
    for task in runtime.list_tasks():
        print(task)

    print("\nAcquire task for Andy:")
    acquired = runtime.acquire_task("Andy")
    print(acquired)

    print("\nYield task for Andy:")
    yielded = runtime.yield_task("Andy", acquired["id"], "finished demo")
    print(yielded)

    reacquired = runtime.acquire_task("Andy")
    print("\nReacquire task-1 to complete it:")
    print(reacquired)

    completed = runtime.complete_task(
        "Andy", reacquired["id"], "prerequisite completed"
    )
    print(completed)

    print("\nAcquire next task after dependency completion:")
    next_task = runtime.acquire_task("Andy")
    print(next_task)


if __name__ == "__main__":
    main()
