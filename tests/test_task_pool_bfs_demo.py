from mindcraft_py.runtime import MindcraftRuntime


def test_get_ready_task_order_returns_dependency_order(tmp_path):
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

[[tasks]]
id = "build_table"
payload = "Build a crafting table"
depends_on = ["craft_planks"]
""",
        encoding="utf-8",
    )

    runtime = MindcraftRuntime()
    runtime.load_task_pool_file(task_file)

    assert runtime.get_ready_task_order() == [
        "gather_oak_logs",
        "craft_planks",
        "build_table",
    ]


def test_acquire_task_by_id_rejects_unready_dependency(tmp_path):
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

    try:
        runtime.acquire_task_by_id("Andy", "craft_planks")
    except Exception as error:
        assert "dependencies are not complete" in str(error)
    else:
        raise AssertionError("Expected dependency failure")
