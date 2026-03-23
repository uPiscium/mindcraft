from pathlib import Path

from mindcraft_py.catalog import build_command_catalog
from mindcraft_py.commands import (
    CommandParam,
    CommandSpec,
    PythonCommandRegistry,
    contains_command,
    execute_action,
    execute_query,
    get_command_docs,
    get_default_registry,
    parse_command_message,
    trunc_command_message,
)
from mindcraft_py.js_command_specs import extract_js_command_specs
from mindcraft_py.profiles import load_profile

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_DEFAULT_COMMANDS = {
    "!stats": {
        "description": "Get your bot's location, health, hunger, and time of day.",
        "params": {},
    },
    "!inventory": {
        "description": "Get your bot's inventory.",
        "params": {},
    },
    "!nearbyBlocks": {
        "description": "Get the blocks near the bot.",
        "params": {},
    },
    "!entities": {
        "description": "Get the nearby players and entities.",
        "params": {},
    },
    "!craftable": {
        "description": "Get the craftable items with the bot's inventory.",
        "params": {},
    },
    "!modes": {
        "description": (
            "Get all available modes and their docs and see which are on/off."
        ),
        "params": {},
    },
    "!savedPlaces": {
        "description": "List all saved locations.",
        "params": {},
    },
    "!checkBlueprintLevel": {
        "description": (
            "Check if the level is complete and what blocks still need to be placed "
            "for the blueprint"
        ),
        "params": {"levelNum": ("int", "The level number to check.")},
    },
    "!checkBlueprint": {
        "description": "Check what blocks still need to be placed for the blueprint",
        "params": {},
    },
    "!getBlueprint": {
        "description": "Get the blueprint for the building",
        "params": {},
    },
    "!getBlueprintLevel": {
        "description": "Get the blueprint for the building",
        "params": {"levelNum": ("int", "The level number to check.")},
    },
    "!getCraftingPlan": {
        "description": (
            "Provides a comprehensive crafting plan for a specified item. This "
            "includes a breakdown of required ingredients, the exact quantities "
            "needed, and an analysis of missing ingredients or extra items needed "
            "based on the bot's current inventory."
        ),
        "params": {
            "targetItem": ("string", "The item that we are trying to craft"),
            "quantity": (
                "int",
                "The quantity of the item that we are trying to craft",
            ),
        },
    },
    "!searchWiki": {
        "description": "Search the Minecraft Wiki for the given query.",
        "params": {"query": ("string", "The query to search for.")},
    },
    "!help": {
        "description": "Lists all available commands and their descriptions.",
        "params": {},
    },
    "!stop": {
        "description": (
            "Force stop all actions and commands that are currently executing."
        ),
        "params": {},
    },
    "!goal": {
        "description": (
            "Set a goal prompt to endlessly work towards with continuous "
            "self-prompting."
        ),
        "params": {"selfPrompt": ("string", "The goal prompt.")},
    },
    "!newAction": {
        "description": (
            "Perform new and unknown custom behaviors that are not available "
            "as a command."
        ),
        "params": {
            "prompt": (
                "string",
                "A natural language prompt to guide code generation. Make a "
                "detailed step-by-step plan.",
            )
        },
    },
}


def test_parse_goal_command():
    invocation = parse_command_message('!goal("collect logs")')

    assert invocation.command_name == "!goal"
    assert invocation.args == ("collect logs",)


def test_contains_and_truncates_command():
    message = 'Plan first, then run !goal("collect logs") and continue'

    assert contains_command(message) == "!goal"
    assert (
        trunc_command_message(message) == 'Plan first, then run !goal("collect logs")'
    )


def test_unknown_command_raises():
    try:
        parse_command_message("!missing()")
    except ValueError as error:
        assert str(error) == "!missing is not a command."
    else:
        raise AssertionError("Expected ValueError for unknown command")


def test_command_docs_respect_blocked_actions():
    docs = get_command_docs(blocked_actions=["!newAction"])

    assert "!stats:" in docs
    assert "!newAction:" not in docs


def test_default_registry_matches_expected_command_specs():
    actual_specs = {
        command.name: command for command in get_default_registry().commands()
    }

    assert set(actual_specs) == set(EXPECTED_DEFAULT_COMMANDS)

    for command_name, expected_spec in EXPECTED_DEFAULT_COMMANDS.items():
        actual_spec = actual_specs[command_name]
        assert actual_spec.description == expected_spec["description"]

        actual_params = actual_spec.params or {}
        expected_params = expected_spec["params"]
        assert set(actual_params) == set(expected_params)

        for param_name, (param_type, description) in expected_params.items():
            actual_param = actual_params[param_name]
            assert actual_param.type == param_type
            assert actual_param.description == description


def test_default_registry_matches_javascript_specs():
    registry = get_default_registry()
    js_specs = extract_js_command_specs(registry.command_names())

    actual_specs = {command.name: command for command in registry.commands()}
    assert set(actual_specs) == set(js_specs)

    for command_name, actual_spec in actual_specs.items():
        js_spec = js_specs[command_name]
        assert actual_spec.description == js_spec.description
        assert actual_spec.kind == js_spec.kind

        actual_params = actual_spec.params or {}
        js_params = js_spec.params or {}
        assert set(actual_params) == set(js_params)

        for param_name, actual_param in actual_params.items():
            js_param = js_params[param_name]
            assert actual_param.type == js_param.type
            assert actual_param.description == js_param.description


def test_command_catalog_is_generated():
    catalog = build_command_catalog()

    assert catalog[0]["name"] == "!stats"
    assert any(item["name"] == "!help" for item in catalog)


def test_command_catalog_matches_python_registry():
    from mindcraft_py.catalog import load_command_catalog

    catalog = load_command_catalog()
    names = [item["name"] for item in catalog]

    assert names == [command.name for command in get_default_registry().commands()]


def test_default_registry_parses_all_expected_command_names():
    docs = get_command_docs()

    for command_name in EXPECTED_DEFAULT_COMMANDS:
        assert f"{command_name}:" in docs


def build_sample_registry():
    return PythonCommandRegistry(
        commands=[
            CommandSpec(
                name="!sample",
                description="Sample command.",
                params={
                    "count": CommandParam(
                        type="int",
                        description="How many.",
                        domain=(1, 5, "[]"),
                    ),
                    "enabled": CommandParam(
                        type="boolean",
                        description="Whether enabled.",
                    ),
                    "distance": CommandParam(
                        type="float",
                        description="Distance value.",
                        domain=(0, 10, "[)"),
                    ),
                },
            )
        ]
    )


def test_parses_typed_arguments():
    registry = build_sample_registry()

    invocation = registry.parse_message("!sample(3, true, 2.5)")

    assert invocation.command_name == "!sample"
    assert invocation.args == (3, True, 2.5)


def test_rejects_wrong_argument_count():
    registry = build_sample_registry()

    try:
        registry.parse_message("!sample(3, true)")
    except ValueError as error:
        assert "requires 3 args" in str(error)
    else:
        raise AssertionError("Expected ValueError for wrong argument count")


def test_rejects_out_of_domain_argument():
    registry = build_sample_registry()

    try:
        registry.parse_message("!sample(7, true, 2.5)")
    except ValueError as error:
        assert "Param 'count' must be an element" in str(error)
    else:
        raise AssertionError("Expected ValueError for out-of-domain argument")


def test_rejects_invalid_boolean_argument():
    registry = build_sample_registry()

    try:
        registry.parse_message('!sample(3, "maybe", 2.5)')
    except ValueError as error:
        assert "Param 'enabled' must be of type boolean" in str(error)
    else:
        raise AssertionError("Expected ValueError for invalid boolean argument")


class FakeRuntime:
    def __init__(self):
        self.calls = []

    def execute_query_command(self, agent_name, message, timeout=60):
        return self.execute_bridge_command("query", agent_name, message, timeout)

    def execute_action_command(self, agent_name, message, timeout=60):
        return self.execute_bridge_command("action", agent_name, message, timeout)

    def execute_bridge_command(self, command_kind, agent_name, message, timeout=60):
        self.calls.append(
            {
                "command_kind": command_kind,
                "agent_name": agent_name,
                "message": message,
                "timeout": timeout,
            }
        )
        return f"{command_kind}:{agent_name}:{message}:{timeout}"


def test_execute_query_uses_runtime_bridge():
    runtime = FakeRuntime()

    result = execute_query(runtime, "Andy", "!stats() trailing text", timeout=15)

    assert result == "query:Andy:!stats:15"
    assert runtime.calls == [
        {
            "command_kind": "query",
            "agent_name": "Andy",
            "message": "!stats",
            "timeout": 15,
        }
    ]


def test_execute_query_rejects_non_query_commands():
    runtime = FakeRuntime()

    try:
        execute_query(runtime, "Andy", '!goal("collect logs")')
    except ValueError as error:
        assert str(error) == "!goal is not a query command."
    else:
        raise AssertionError("Expected ValueError for non-query command execution")


def test_execute_action_uses_runtime_bridge():
    runtime = FakeRuntime()

    result = execute_action(runtime, "Andy", '!goal("collect logs")', timeout=15)

    assert result == 'action:Andy:!goal("collect logs"):15'
    assert runtime.calls == [
        {
            "command_kind": "action",
            "agent_name": "Andy",
            "message": '!goal("collect logs")',
            "timeout": 15,
        }
    ]


def test_execute_action_rejects_non_action_commands():
    runtime = FakeRuntime()

    try:
        execute_action(runtime, "Andy", "!stats()")
    except ValueError as error:
        assert str(error) == "!stats is not a action command."
    else:
        raise AssertionError("Expected ValueError for non-action command execution")


def test_load_profile_supports_json_and_toml():
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    json_profile = load_profile(project_root / "agents" / "Andy.json")
    toml_profile = load_profile(project_root / "agents" / "Andy.toml")

    assert json_profile["name"] == "Andy"
    assert toml_profile["name"] == "Andy"
    assert json_profile["model"]["api"] == toml_profile["model"]["api"]
