from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mindcraft_py.runtime import MindcraftRuntime

TaskExecutor = Callable[[dict[str, Any]], Any]


def _priority_key(task: dict[str, Any]) -> tuple[int, str]:
    return int(task.get("priority", 0)), str(task.get("id", ""))


def _build_dependency_maps(
    tasks: list[dict[str, Any]],
) -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    remaining_dependencies: dict[str, set[str]] = {}
    dependents: dict[str, list[str]] = {}

    for task in tasks:
        task_id = str(task["id"])
        dependencies = {str(dep) for dep in task.get("depends_on", [])}
        remaining_dependencies[task_id] = dependencies
        for dependency_id in dependencies:
            dependents.setdefault(dependency_id, []).append(task_id)

    return remaining_dependencies, dependents


def _normalize_executor_result(task: dict[str, Any], result: Any) -> tuple[bool, str]:
    if isinstance(result, dict):
        success = bool(result.get("success", True))
        reason = str(
            result.get("reason")
            or result.get("message")
            or (
                f"task {task['id']} completed"
                if success
                else f"task {task['id']} failed"
            )
        )
        return success, reason

    if result is False:
        return False, f"task {task['id']} failed"

    if isinstance(result, str) and result.strip():
        return True, result.strip()

    return True, f"task {task['id']} completed"


def default_task_executor(task: dict[str, Any]) -> dict[str, Any]:
    payload = task.get("payload") or task.get("goal") or ""
    print(f"Executing task {task['id']}: {payload}")
    return {"success": True, "reason": f"task {task['id']} completed"}


def run_dependency_bfs(
    runtime: MindcraftRuntime,
    requester_id: str = "agent",
    executor: TaskExecutor | None = None,
    stop_on_failure: bool = True,
) -> dict[str, list[str]]:
    tasks = {task["id"]: task for task in runtime.list_tasks()}
    if not tasks:
        return {"executed": [], "completed": [], "failed": []}

    remaining_dependencies, dependents = _build_dependency_maps(list(tasks.values()))
    ready = sorted(
        [task_id for task_id, deps in remaining_dependencies.items() if not deps],
        key=lambda task_id: _priority_key(tasks[task_id]),
    )

    executed: list[str] = []
    completed: list[str] = []
    failed: list[str] = []
    executor = executor or default_task_executor

    while ready:
        task_id = ready.pop(0)
        if task_id in executed:
            continue

        task = runtime.acquire_task_by_id(requester_id, task_id)
        try:
            result = executor(task)
        except Exception as error:  # pragma: no cover - defensive path
            runtime.yield_task(requester_id, task_id, str(error))
            failed.append(task_id)
            executed.append(task_id)
            if stop_on_failure:
                raise
            continue

        success, reason = _normalize_executor_result(task, result)
        if success:
            runtime.complete_task(requester_id, task_id, reason)
            completed.append(task_id)
            executed.append(task_id)

            for child_task_id in dependents.get(task_id, []):
                remaining_dependencies[child_task_id].discard(task_id)
                if (
                    not remaining_dependencies[child_task_id]
                    and child_task_id not in executed
                ):
                    ready.append(child_task_id)
            ready.sort(key=lambda child_id: _priority_key(tasks[child_id]))
            continue

        runtime.yield_task(requester_id, task_id, reason)
        failed.append(task_id)
        executed.append(task_id)
        if stop_on_failure:
            raise RuntimeError(reason)

    unresolved = [
        task_id
        for task_id, deps in remaining_dependencies.items()
        if task_id not in executed and deps
    ]

    return {
        "executed": executed,
        "completed": completed,
        "failed": failed,
        "unresolved": sorted(unresolved),
    }
