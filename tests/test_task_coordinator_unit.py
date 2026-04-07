from mindcraft_py.task_coordinator import (
    AVAILABLE,
    FAST_COMPUTE,
    HIGH_VRAM,
    LOCKED,
    CentralTaskCoordinator,
)


def test_register_task_overwrites_existing_task_and_keeps_single_entry():
    coordinator = CentralTaskCoordinator()

    first = coordinator.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "old"}
    )
    second = coordinator.register_task(
        {"id": "task-1", "capability_level": FAST_COMPUTE, "payload": "new"}
    )

    assert first["payload"] == "old"
    assert second["payload"] == "new"
    assert coordinator.list_tasks() == [second]


def test_register_task_assigns_monotonic_priority_when_missing():
    coordinator = CentralTaskCoordinator()

    first = coordinator.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "a"}
    )
    second = coordinator.register_task(
        {"id": "task-2", "capability_level": HIGH_VRAM, "payload": "b"}
    )

    assert first["priority"] == 1
    assert second["priority"] == 2


def test_acquire_task_prefers_lower_capability_then_priority_then_id():
    coordinator = CentralTaskCoordinator()
    coordinator.register_task(
        {
            "id": "task-b",
            "capability_level": FAST_COMPUTE,
            "payload": "b",
            "priority": 2,
        }
    )
    coordinator.register_task(
        {
            "id": "task-a",
            "capability_level": FAST_COMPUTE,
            "payload": "a",
            "priority": 2,
        }
    )
    coordinator.register_task(
        {
            "id": "task-c",
            "capability_level": HIGH_VRAM,
            "payload": "c",
            "priority": 1,
        }
    )

    acquired = coordinator.acquire_task("agent-a", FAST_COMPUTE)

    assert acquired["id"] == "task-c"
    assert acquired["state"] == LOCKED
    assert acquired["lock_metadata"]["requester_id"] == "agent-a"


def test_expire_locks_releases_only_stale_tasks_and_records_timeout_history(
    monkeypatch,
):
    coordinator = CentralTaskCoordinator()
    coordinator.register_task(
        {
            "id": "old-task",
            "capability_level": HIGH_VRAM,
            "payload": "old",
            "state": LOCKED,
            "lock_metadata": {"requester_id": "agent-a", "locked_at": 900.0},
        }
    )
    coordinator.register_task(
        {
            "id": "recent-task",
            "capability_level": HIGH_VRAM,
            "payload": "recent",
            "state": LOCKED,
            "lock_metadata": {"requester_id": "agent-b", "locked_at": 995.0},
        }
    )

    monkeypatch.setattr("mindcraft_py.task_coordinator.time", lambda: 1000.0)

    released = coordinator.expire_locks(10)

    tasks = {task["id"]: task for task in coordinator.list_tasks()}
    assert released == 1
    assert tasks["old-task"]["state"] == AVAILABLE
    assert tasks["old-task"]["history"][-1]["reason"] == "lock timeout"
    assert tasks["recent-task"]["state"] == LOCKED


def test_clear_removes_all_registered_tasks():
    coordinator = CentralTaskCoordinator()
    coordinator.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "a"}
    )

    coordinator.clear()

    assert coordinator.list_tasks() == []
