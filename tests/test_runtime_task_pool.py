from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_coordinator import AVAILABLE, FAST_COMPUTE, HIGH_VRAM, LOCKED


def test_register_task_keeps_registered_task():
    runtime = MindcraftRuntime()

    task = runtime.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "mine logs"}
    )

    assert task["id"] == "task-1"
    assert task["state"] == AVAILABLE


def test_list_tasks_returns_registered_tasks():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "mine logs"}
    )

    assert runtime.list_tasks()[0]["id"] == "task-1"


def test_acquire_task_locks_matching_task():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "a"}
    )

    task = runtime.acquire_task("agent-a", FAST_COMPUTE)

    assert task["id"] == "task-1"
    assert task["state"] == LOCKED


def test_acquire_task_prefers_higher_priority_task():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {
            "id": "task-low",
            "capability_level": FAST_COMPUTE,
            "payload": "a",
            "priority": 2,
        }
    )
    runtime.register_task(
        {
            "id": "task-high",
            "capability_level": HIGH_VRAM,
            "payload": "b",
            "priority": 1,
        }
    )

    task = runtime.acquire_task("agent-a", FAST_COMPUTE)

    assert task["id"] == "task-high"


def test_yield_task_rejects_wrong_owner():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "a"}
    )
    runtime.acquire_task("agent-a", HIGH_VRAM)

    try:
        runtime.yield_task("agent-b", "task-1", "wrong owner")
    except Exception as error:
        assert "different requester" in str(error)
    else:
        raise AssertionError("Expected ownership error")


def test_yield_task_restores_availability_and_history():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {"id": "task-1", "capability_level": HIGH_VRAM, "payload": "a"}
    )
    runtime.acquire_task("agent-a", HIGH_VRAM)

    result = runtime.yield_task("agent-a", "task-1", "done")

    assert result["task"]["state"] == AVAILABLE
    assert result["task"]["history"][-1]["reason"] == "done"
