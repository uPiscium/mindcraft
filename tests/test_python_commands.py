from mindcraft_py.commands import (
    CommandParam,
    CommandSpec,
    PythonCommandRegistry,
    contains_command,
    get_command_docs,
    parse_command_message,
    trunc_command_message,
)

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
    registry = PythonCommandRegistry()
    for command_name, command_spec in EXPECTED_DEFAULT_COMMANDS.items():
        registry.register(
            CommandSpec(
                name=command_name,
                description=command_spec["description"],
                params={
                    param_name: CommandParam(type=param_type, description=description)
                    for param_name, (param_type, description) in command_spec[
                        "params"
                    ].items()
                }
                or None,
            )
        )

    expected_docs = registry.get_command_docs()
    actual_docs = get_command_docs()

    assert actual_docs == expected_docs


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
