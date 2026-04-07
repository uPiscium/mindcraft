from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from time import time
from typing import Any

AVAILABLE = "AVAILABLE"
LOCKED = "LOCKED"
COMPLETED = "COMPLETED"
FAILED = "FAILED"


@dataclass
class TaskEntity:
    id: str
    payload: str
    state: str = AVAILABLE
    depends_on: list[str] = field(default_factory=list)
    lock_metadata: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    priority: int = 0


class TaskCoordinatorError(RuntimeError):
    pass


class ConflictError(TaskCoordinatorError):
    pass


class TaskNotFoundError(TaskCoordinatorError):
    pass


class TaskOwnershipError(TaskCoordinatorError):
    pass


class CentralTaskCoordinator:
    def __init__(self, tasks: list[TaskEntity | dict[str, Any]] | None = None):
        self._lock = RLock()
        self._tasks: dict[str, TaskEntity] = {}
        self._next_priority = 0
        for task in tasks or []:
            self.register_task(task)

    def register_task(
        self,
        task: TaskEntity | dict[str, Any] | None = None,
        **task_fields: Any,
    ) -> dict[str, Any]:
        with self._lock:
            entity = self._coerce_task(task, task_fields)
            if entity.priority == 0:
                self._next_priority += 1
                entity.priority = self._next_priority
            self._tasks[entity.id] = entity
            return self._serialize_task(entity)

    add_task = register_task

    def acquire_task(self, requester_id: str) -> dict[str, Any]:
        with self._lock:
            eligible = [
                task
                for task in self._tasks.values()
                if task.state == AVAILABLE and self._dependencies_complete(task)
            ]
            if not eligible:
                raise ConflictError("No available task matches the request.")

            task = sorted(
                eligible,
                key=lambda item: (item.priority, item.id),
            )[0]
            task.state = LOCKED
            task.lock_metadata = {
                "requester_id": requester_id,
                "locked_at": time(),
            }
            return self._serialize_task(task)

    def yield_task(
        self, requester_id: str, task_id: str, reason: str
    ) -> dict[str, Any]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task '{task_id}' not found.")
            if task.state != LOCKED:
                raise TaskOwnershipError(f"Task '{task_id}' is not locked.")
            if (task.lock_metadata or {}).get("requester_id") != requester_id:
                raise TaskOwnershipError("Task is locked by a different requester.")

            task.history.append(
                {
                    "reason": reason,
                    "requester_id": requester_id,
                    "recorded_at": time(),
                }
            )
            task.state = AVAILABLE
            task.lock_metadata = None
            return {"success": True, "task": self._serialize_task(task)}

    def expire_locks(self, max_lock_age_seconds: float) -> int:
        with self._lock:
            now = time()
            released = 0
            for task in self._tasks.values():
                metadata = task.lock_metadata or {}
                if task.state != LOCKED:
                    continue
                locked_at = metadata.get("locked_at")
                if locked_at is None or now - float(locked_at) <= max_lock_age_seconds:
                    continue
                task.state = AVAILABLE
                task.lock_metadata = None
                task.history.append(
                    {
                        "reason": "lock timeout",
                        "requester_id": metadata.get("requester_id"),
                        "recorded_at": now,
                    }
                )
                released += 1
            return released

    def list_tasks(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self._serialize_task(task) for task in self._tasks.values()]

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()

    def _coerce_task(
        self,
        task: TaskEntity | dict[str, Any] | None,
        task_fields: dict[str, Any],
    ) -> TaskEntity:
        if isinstance(task, TaskEntity):
            return task

        data: dict[str, Any] = {}
        if task is not None:
            data.update(task)
        data.update(task_fields)

        task_id = str(data.get("id") or data.get("task_id") or "").strip()
        if not task_id:
            raise ValueError("Task id is required.")

        payload = str(data.get("payload", ""))
        state = str(data.get("state", AVAILABLE))
        depends_on = [str(dep) for dep in data.get("depends_on", [])]
        lock_metadata = data.get("lock_metadata")
        history = list(data.get("history", []))
        priority_value = data.get("priority")
        priority = int(priority_value) if priority_value is not None else 0

        return TaskEntity(
            id=task_id,
            payload=payload,
            state=state,
            depends_on=depends_on,
            lock_metadata=lock_metadata,
            history=history,
            priority=priority,
        )

    def _dependencies_complete(self, task: TaskEntity) -> bool:
        for dependency_id in task.depends_on:
            dependency = self._tasks.get(dependency_id)
            if dependency is None or dependency.state != COMPLETED:
                return False
        return True

    def _serialize_task(self, task: TaskEntity) -> dict[str, Any]:
        return {
            "id": task.id,
            "state": task.state,
            "payload": task.payload,
            "depends_on": list(task.depends_on),
            "lock_metadata": task.lock_metadata,
            "history": list(task.history),
            "priority": task.priority,
        }


AcquireTask = CentralTaskCoordinator.acquire_task
YieldTask = CentralTaskCoordinator.yield_task
