import pytest

from mindcraft_py.task_coordinator import (
    AVAILABLE,
    FAST_COMPUTE,
    HIGH_VRAM,
    LOCKED,
    CentralTaskCoordinator,
    ConflictError,
    TaskEntity,
    TaskOwnershipError,
)


def test_acquire_task_locks_best_matching_task():
    coordinator = CentralTaskCoordinator(
        [
            TaskEntity("task-2", FAST_COMPUTE, "b"),
            TaskEntity("task-1", HIGH_VRAM, "a"),
        ]
    )

    task = coordinator.acquire_task("agent-a", FAST_COMPUTE)

    assert task["id"] == "task-1"
    assert task["state"] == LOCKED
    assert task["lock_metadata"]["requester_id"] == "agent-a"


def test_acquire_task_raises_conflict_when_no_match():
    coordinator = CentralTaskCoordinator([TaskEntity("task-1", HIGH_VRAM, "a")])

    with pytest.raises(ConflictError):
        coordinator.acquire_task("agent-a", 0)


def test_yield_task_restores_availability_and_records_history():
    coordinator = CentralTaskCoordinator([TaskEntity("task-1", HIGH_VRAM, "a")])
    coordinator.acquire_task("agent-a", HIGH_VRAM)

    result = coordinator.yield_task("agent-a", "task-1", "need to retry")

    assert result["success"] is True
    assert result["task"]["state"] == AVAILABLE
    assert result["task"]["history"][-1]["reason"] == "need to retry"


def test_yield_task_rejects_wrong_owner():
    coordinator = CentralTaskCoordinator([TaskEntity("task-1", HIGH_VRAM, "a")])
    coordinator.acquire_task("agent-a", HIGH_VRAM)

    with pytest.raises(TaskOwnershipError):
        coordinator.yield_task("agent-b", "task-1", "nope")
