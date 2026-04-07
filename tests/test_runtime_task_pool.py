from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_coordinator import AVAILABLE, LOCKED


def test_register_task_keeps_registered_task():
    runtime = MindcraftRuntime()

    task = runtime.register_task(
        {"id": "task-1", "payload": "mine logs", "depends_on": []}
    )

    assert task["id"] == "task-1"
    assert task["state"] == AVAILABLE


def test_list_tasks_returns_registered_tasks():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "mine logs", "depends_on": []})

    assert runtime.list_tasks()[0]["id"] == "task-1"


def test_acquire_task_locks_matching_task():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a", "depends_on": []})

    task = runtime.acquire_task("agent-a")

    assert task["id"] == "task-1"
    assert task["state"] == LOCKED


def test_acquire_task_prefers_higher_priority_task():
    runtime = MindcraftRuntime()
    runtime.register_task(
        {
            "id": "task-low",
            "payload": "a",
            "depends_on": [],
            "priority": 2,
        }
    )
    runtime.register_task(
        {
            "id": "task-high",
            "payload": "b",
            "depends_on": [],
            "priority": 1,
        }
    )

    task = runtime.acquire_task("agent-a")

    assert task["id"] == "task-high"


def test_yield_task_rejects_wrong_owner():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a", "depends_on": []})
    runtime.acquire_task("agent-a")

    try:
        runtime.yield_task("agent-b", "task-1", "wrong owner")
    except Exception as error:
        assert "different requester" in str(error)
    else:
        raise AssertionError("Expected ownership error")


def test_yield_task_restores_availability_and_history():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a", "depends_on": []})
    runtime.acquire_task("agent-a")

    result = runtime.yield_task("agent-a", "task-1", "done")

    assert result["task"]["state"] == AVAILABLE
    assert result["task"]["history"][-1]["reason"] == "done"
