from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_execution_controller import TaskExecutionController, TaskExecutor


def test_task_execution_controller_completes_task(tmp_path):
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

    controller = TaskExecutionController(runtime)
    result = controller.run("Andy", "gather_oak_logs")

    assert result.success is True
    assert result.steps[0]["step"]["content"] == "Collect logs"
    assert runtime.list_tasks()[0]["state"] == "COMPLETED"


def test_task_execution_controller_yields_on_failed_step(tmp_path):
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

    class FailingExecutor(TaskExecutor):
        def execute_step(self, step):
            return {"success": False, "reason": "blocked"}

    controller = TaskExecutionController(runtime, executor=FailingExecutor())
    result = controller.run("Andy", "gather_oak_logs")

    assert result.success is False
    assert result.reason == "blocked"
    assert runtime.list_tasks()[0]["state"] == "AVAILABLE"
