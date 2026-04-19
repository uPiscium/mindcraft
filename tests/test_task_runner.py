from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_runner import run_dependency_bfs


def test_run_dependency_bfs_executes_tasks_in_dependency_order(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "gather_oak_logs"
payload = "Collect logs"
priority = 1

[[tasks]]
id = "craft_planks"
payload = "Craft planks"
depends_on = ["gather_oak_logs"]
priority = 2

[[tasks]]
id = "build_table"
payload = "Build a crafting table"
depends_on = ["craft_planks"]
priority = 3
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(task_file)

    observed = []

    def executor(task):
        observed.append(task["id"])
        return {"success": True, "reason": f"done {task['id']}"}

    result = run_dependency_bfs(runtime, executor=executor)

    assert observed == ["gather_oak_logs", "craft_planks", "build_table"]
    assert result["completed"] == ["gather_oak_logs", "craft_planks", "build_table"]


def test_run_dependency_bfs_yields_and_stops_on_failure(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "gather_oak_logs"
payload = "Collect logs"

[[tasks]]
id = "craft_planks"
payload = "Craft planks"
depends_on = ["gather_oak_logs"]
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(task_file)

    def executor(task):
        if task["id"] == "gather_oak_logs":
            return {"success": False, "reason": "blocked"}
        return {"success": True}

    result = run_dependency_bfs(runtime, executor=executor, stop_on_failure=False)

    assert result["completed"] == []
    assert result["failed"] == ["gather_oak_logs"]
    assert result["unresolved"] == ["craft_planks"]
