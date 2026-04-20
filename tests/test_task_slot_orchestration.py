from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_slot import ASSIGNED, COMPLETED, EMPTY
from mindcraft_py.task_slot_orchestrator import TaskOrchestrator


def test_slot_is_empty_before_assignment():
    runtime = MindcraftRuntime()
    slot = runtime.get_task_slot("Andy")

    assert slot.state == EMPTY
    assert slot.is_empty() is True


def test_task_assignment_moves_slot_to_assigned(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "gather_oak_logs"
payload = "Collect logs"
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(task_file)
    runtime.agent_processes["Andy"] = {"agent_process": object()}

    task = runtime.acquire_task_for_agent("Andy")

    slot = runtime.get_task_slot("Andy")
    assert task["id"] == "gather_oak_logs"
    assert slot.state == ASSIGNED
    assert slot.task["id"] == "gather_oak_logs"


def test_orchestrator_runs_assigned_task_to_completion(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "gather_oak_logs"
payload = "Collect logs"
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(task_file)
    runtime.agent_processes["Andy"] = {"agent_process": object()}
    runtime.acquire_task_for_agent("Andy")

    orchestrator = TaskOrchestrator(runtime)
    result = orchestrator.tick("Andy")

    assert result["status"] == COMPLETED
    assert runtime.get_task_slot("Andy").state == EMPTY
    assert runtime.list_tasks()[0]["state"] == COMPLETED
