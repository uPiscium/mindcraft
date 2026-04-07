import pytest

from mindcraft_py.task_coordinator import (
    AVAILABLE,
    COMPLETED,
    LOCKED,
    CentralTaskCoordinator,
    ConflictError,
    TaskEntity,
    TaskOwnershipError,
)


def test_acquire_task_locks_best_matching_task():
    coordinator = CentralTaskCoordinator(
        [
            TaskEntity("task-2", "b", state=COMPLETED),
            TaskEntity("task-1", "a", depends_on=["task-2"]),
        ]
    )

    task = coordinator.acquire_task("agent-a")

    assert task["id"] == "task-1"
    assert task["state"] == LOCKED
    assert task["lock_metadata"]["requester_id"] == "agent-a"


def test_acquire_task_raises_conflict_when_no_match():
    coordinator = CentralTaskCoordinator(
        [TaskEntity("task-1", "a", depends_on=["missing"])]
    )

    with pytest.raises(ConflictError):
        coordinator.acquire_task("agent-a")


def test_yield_task_restores_availability_and_records_history():
    coordinator = CentralTaskCoordinator([TaskEntity("task-1", "a")])
    coordinator.acquire_task("agent-a")

    result = coordinator.yield_task("agent-a", "task-1", "need to retry")

    assert result["success"] is True
    assert result["task"]["state"] == AVAILABLE
    assert result["task"]["history"][-1]["reason"] == "need to retry"


def test_yield_task_rejects_wrong_owner():
    coordinator = CentralTaskCoordinator([TaskEntity("task-1", "a")])
    coordinator.acquire_task("agent-a")

    with pytest.raises(TaskOwnershipError):
        coordinator.yield_task("agent-b", "task-1", "nope")
