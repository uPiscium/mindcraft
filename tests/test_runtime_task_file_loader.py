import pytest

from mindcraft_py.runtime import MindcraftRuntime


def test_load_task_pool_file_registers_tasks_with_dependencies(tmp_path):
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
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    registered = runtime.load_task_pool_file(task_file)

    assert [task["id"] for task in registered] == ["gather_oak_logs", "craft_planks"]
    assert runtime.list_tasks()[1]["depends_on"] == ["gather_oak_logs"]


def test_load_task_pool_file_rejects_missing_file(tmp_path):
    runtime = MindcraftRuntime()

    with pytest.raises(FileNotFoundError):
        runtime.load_task_pool_file(tmp_path / "missing.toml")


def test_load_task_pool_file_rejects_non_task_array(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text("title = 'broken'", encoding="utf-8")

    runtime = MindcraftRuntime()

    with pytest.raises(ValueError):
        runtime.load_task_pool_file(task_file)


def test_load_task_pool_file_validates_missing_dependencies(tmp_path):
    task_file = tmp_path / "task_pool.toml"
    task_file.write_text(
        """
[[tasks]]
id = "craft_planks"
payload = "Craft planks"
depends_on = ["gather_oak_logs"]
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()

    with pytest.raises(ValueError):
        runtime.load_task_pool_file(task_file)


def test_create_agent_seeds_task_pool_file_from_profile(tmp_path):
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
    runtime.create_agent(
        {
            "profile": {"name": "Andy", "task_pool_file": str(task_file)},
            "viewer_port": 0,
        }
    )

    assert runtime.list_tasks()[0]["id"] == "gather_oak_logs"


def test_create_agent_keeps_existing_task_pool_when_tasks_are_seeded(tmp_path):
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
    runtime.create_agent(
        {
            "profile": {"name": "Andy", "task_pool_file": str(task_file)},
            "viewer_port": 0,
        }
    )

    assert runtime.list_tasks()[0]["id"] == "gather_oak_logs"
