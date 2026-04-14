from mindcraft_py.runtime import MindcraftRuntime


def test_create_agent_seeds_tasks_from_settings():
    runtime = MindcraftRuntime()

    runtime.create_agent(
        {
            "profile": {"name": "Andy", "tasks": [{"id": "task-1", "payload": "a"}]},
            "viewer_port": 0,
        }
    )

    assert runtime.list_tasks()[0]["id"] == "task-1"


def test_acquire_task_for_agent_records_current_task():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a"})
    runtime.agent_processes["Andy"] = {"agent_process": object()}

    task = runtime.acquire_task_for_agent("Andy")

    assert task["id"] == "task-1"
    assert runtime.agent_tasks["Andy"]["id"] == "task-1"


def test_yield_task_for_agent_clears_current_task():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a"})
    runtime.agent_processes["Andy"] = {"agent_process": object()}
    runtime.acquire_task_for_agent("Andy")

    result = runtime.yield_task_for_agent("Andy", "done")

    assert result["task"]["state"] == "AVAILABLE"
    assert "Andy" not in runtime.agent_tasks


def test_complete_task_for_agent_marks_task_completed():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a"})
    runtime.agent_processes["Andy"] = {"agent_process": object()}
    runtime.acquire_task_for_agent("Andy")

    result = runtime.complete_task_for_agent("Andy", "done")

    assert result["task"]["state"] == "COMPLETED"
    assert "Andy" not in runtime.agent_tasks


def test_stop_agent_by_name_yields_locked_task():
    runtime = MindcraftRuntime()
    runtime.register_task({"id": "task-1", "payload": "a"})

    class FakeAgentProcess:
        def stop(self):
            return None

    runtime.agent_processes["Andy"] = {"agent_process": FakeAgentProcess()}
    runtime.acquire_task_for_agent("Andy")

    runtime.stop_agent_by_name("Andy")

    assert runtime.list_tasks()[0]["state"] == "AVAILABLE"
