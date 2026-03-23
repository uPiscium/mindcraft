import json
from pathlib import Path

from mindcraft_py.profiles import load_profile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASK_PATH = PROJECT_ROOT / "tasks" / "multiagent_crafting_tasks.json"


def test_multiagent_shears_task_has_inventory_initialization():
    task = json.loads(TASK_PATH.read_text(encoding="utf-8"))[
        "multiagent_techtree_1_shears"
    ]

    assert task["agent_count"] == 2
    assert task["initial_inventory"]["0"]["iron_ingot"] == 1
    assert task["initial_inventory"]["1"]["iron_ingot"] == 1
    assert task["initial_inventory"]["1"]["crafting_table"] == 1


def test_toml_profiles_are_loadable_for_multiagent_runs():
    andy = load_profile(PROJECT_ROOT / "agents" / "Andy.toml")
    assert andy["name"] == "Andy"
