from typing import Any, cast

from mindcraft_py.runtime import MindcraftRuntime


class FakeTaskPool:
    def __init__(self):
        self.calls = []

    def register_task(self, task=None, **task_fields):
        self.calls.append(("register_task", task, task_fields))
        return {"id": "task-1"}

    def list_tasks(self):
        self.calls.append(("list_tasks",))
        return [{"id": "task-1"}]

    def acquire_task(self, requester_id):
        self.calls.append(("acquire_task", requester_id))
        return {"id": "task-1", "state": "LOCKED"}

    def yield_task(self, requester_id, task_id, reason):
        self.calls.append(("yield_task", requester_id, task_id, reason))
        return {"success": True}

    def clear(self):
        self.calls.append(("clear",))


def test_runtime_register_task_delegates_to_task_pool():
    runtime = MindcraftRuntime()
    runtime_any = cast(Any, runtime)
    runtime_any.task_pool = FakeTaskPool()

    result = runtime.register_task({"id": "task-1"}, payload="hello")

    assert result == {"id": "task-1"}
    assert runtime_any.task_pool.calls == [
        ("register_task", {"id": "task-1"}, {"payload": "hello"}),
    ]


def test_runtime_list_tasks_delegates_to_task_pool():
    runtime = MindcraftRuntime()
    runtime_any = cast(Any, runtime)
    runtime_any.task_pool = FakeTaskPool()

    result = runtime.list_tasks()

    assert result == [{"id": "task-1"}]
    assert runtime_any.task_pool.calls == [("list_tasks",)]


def test_runtime_acquire_task_delegates_to_task_pool():
    runtime = MindcraftRuntime()
    runtime_any = cast(Any, runtime)
    runtime_any.task_pool = FakeTaskPool()

    result = runtime.acquire_task("agent-a")

    assert result == {"id": "task-1", "state": "LOCKED"}
    assert runtime_any.task_pool.calls == [("acquire_task", "agent-a")]


def test_runtime_yield_task_delegates_to_task_pool():
    runtime = MindcraftRuntime()
    runtime_any = cast(Any, runtime)
    runtime_any.task_pool = FakeTaskPool()

    result = runtime.yield_task("agent-a", "task-1", "done")

    assert result == {"success": True}
    assert runtime_any.task_pool.calls == [("yield_task", "agent-a", "task-1", "done")]


def test_runtime_shutdown_clears_task_pool():
    runtime = MindcraftRuntime()
    runtime_any = cast(Any, runtime)
    runtime_any.task_pool = FakeTaskPool()

    runtime.shutdown()

    assert runtime_any.task_pool.calls == [("clear",)]
