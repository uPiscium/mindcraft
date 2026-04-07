from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class CommandParam:
    type: str
    description: str
    domain: tuple | None = None


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str
    params: dict[str, CommandParam] | None = None
    kind: str = "query"


@dataclass(frozen=True)
class CommandInvocation:
    command_name: str
    args: tuple


@dataclass(frozen=True)
class CommandRegistrySpec:
    description: str
    kind: str
    params: dict[str, CommandParam]


_DEFAULT_COMMAND_SPECS = [
    CommandSpec("!stats", "Get your bot's location, health, hunger, and time of day."),
    CommandSpec("!inventory", "Get your bot's inventory."),
    CommandSpec("!nearbyBlocks", "Get the blocks near the bot."),
    CommandSpec("!entities", "Get the nearby players and entities."),
    CommandSpec("!craftable", "Get the craftable items with the bot's inventory."),
    CommandSpec(
        "!modes", "Get all available modes and their docs and see which are on/off."
    ),
    CommandSpec("!savedPlaces", "List all saved locations."),
    CommandSpec(
        "!checkBlueprintLevel",
        (
            "Check if the level is complete and what blocks still need to be "
            "placed for the blueprint"
        ),
        params={"levelNum": CommandParam("int", "The level number to check.")},
    ),
    CommandSpec(
        "!checkBlueprint", "Check what blocks still need to be placed for the blueprint"
    ),
    CommandSpec("!getBlueprint", "Get the blueprint for the building"),
    CommandSpec(
        "!getBlueprintLevel",
        "Get the blueprint for the building",
        params={"levelNum": CommandParam("int", "The level number to check.")},
    ),
    CommandSpec(
        "!getCraftingPlan",
        (
            "Provides a comprehensive crafting plan for a specified item. This "
            "includes a breakdown of required ingredients, the exact quantities "
            "needed, and an analysis of missing ingredients or extra items "
            "needed based on the bot's current inventory."
        ),
        params={
            "targetItem": CommandParam(
                "string", "The item that we are trying to craft"
            ),
            "quantity": CommandParam(
                "int", "The quantity of the item that we are trying to craft"
            ),
        },
    ),
    CommandSpec(
        "!searchWiki",
        "Search the Minecraft Wiki for the given query.",
        params={"query": CommandParam("string", "The query to search for.")},
    ),
    CommandSpec("!help", "Lists all available commands and their descriptions."),
    CommandSpec(
        "!stop",
        "Force stop all actions and commands that are currently executing.",
        kind="action",
    ),
    CommandSpec(
        "!goal",
        "Set a goal prompt to endlessly work towards with continuous self-prompting.",
        params={"selfPrompt": CommandParam("string", "The goal prompt.")},
        kind="action",
    ),
    CommandSpec(
        "!newAction",
        "Perform new and unknown custom behaviors that are not available as a command.",
        params={
            "prompt": CommandParam(
                "string",
                (
                    "A natural language prompt to guide code generation. Make "
                    "a detailed step-by-step plan."
                ),
            )
        },
        kind="action",
    ),
]


class PythonCommandRegistry:
    def __init__(self, commands):
        self._commands = list(commands)

    def commands(self):
        return list(self._commands)

    def command_names(self):
        return [command.name for command in self._commands]

    def parse_message(self, message):
        return _parse_command_message(message, self._commands)


def contains_command(message):
    match = re.search(r"![A-Za-z_][A-Za-z0-9_]*", message)
    return match.group(0) if match else None


def _parse_args(arg_text):
    if not arg_text.strip():
        return ()
    normalized = (
        arg_text.replace("true", "True")
        .replace("false", "False")
        .replace("null", "None")
    )
    expr = ast.parse(f"f({normalized})", mode="eval")
    call = cast(ast.Call, expr.body)
    return tuple(ast.literal_eval(arg) for arg in call.args)


def _validate_args(spec, args):
    params = list((spec.params or {}).items())
    if len(args) != len(params):
        raise ValueError(f"{spec.name} requires {len(params)} args.")

    for (param_name, param_spec), value in zip(params, args, strict=True):
        if param_spec.type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Param '{param_name}' must be of type boolean")
        if param_spec.type == "int" and not isinstance(value, int):
            raise ValueError(f"Param '{param_name}' must be of type int")
        if param_spec.type == "float" and not isinstance(value, (int, float)):
            raise ValueError(f"Param '{param_name}' must be of type float")
        if param_spec.domain is not None:
            if len(param_spec.domain) == 3 and isinstance(value, (int, float)):
                lower, upper, bounds = param_spec.domain
                lower_ok = value > lower if bounds[0] == "(" else value >= lower
                upper_ok = value < upper if bounds[1] == ")" else value <= upper
                if not (lower_ok and upper_ok):
                    raise ValueError(f"Param '{param_name}' must be an element")
            elif value not in set(param_spec.domain[:-1]):
                raise ValueError(f"Param '{param_name}' must be an element")


def _parse_command_message(message, commands):
    command_name = contains_command(message)
    if not command_name:
        raise ValueError("No command found.")

    spec = next((cmd for cmd in commands if cmd.name == command_name), None)
    if spec is None:
        raise ValueError(f"{command_name} is not a command.")

    match = re.match(r"(![A-Za-z_][A-Za-z0-9_]*)(?:\((.*)\))?", message.strip())
    args = _parse_args(match.group(2) or "") if match else ()
    _validate_args(spec, args)
    return CommandInvocation(command_name, args)


def parse_command_message(message):
    return _parse_command_message(message, _DEFAULT_COMMAND_SPECS)


def trunc_command_message(message):
    command_name = contains_command(message)
    if not command_name:
        return message
    start = message.find(command_name)
    suffix = message[start + len(command_name) :]
    if not suffix.startswith("("):
        return message[: start + len(command_name)]

    depth = 0
    for index, char in enumerate(suffix):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return message[: start + len(command_name) + index + 1]
    return message[: start + len(command_name)]


def get_command_docs(blocked_actions=None):
    blocked_actions = set(blocked_actions or [])
    docs = []
    for command in _DEFAULT_COMMAND_SPECS:
        if command.name in blocked_actions:
            continue
        docs.append(f"{command.name}: {command.description}")
    return "\n".join(docs)


def get_default_registry():
    return PythonCommandRegistry(_DEFAULT_COMMAND_SPECS)


def get_default_command_specs():
    return list(_DEFAULT_COMMAND_SPECS)


def execute_query(runtime, agent_name, message, timeout=60):
    invocation = parse_command_message(message)
    query_commands = {
        "!stats",
        "!inventory",
        "!nearbyBlocks",
        "!entities",
        "!craftable",
        "!modes",
        "!savedPlaces",
        "!checkBlueprintLevel",
        "!checkBlueprint",
        "!getBlueprint",
        "!getBlueprintLevel",
        "!getCraftingPlan",
        "!searchWiki",
        "!help",
    }
    if invocation.command_name not in query_commands:
        raise ValueError(f"{invocation.command_name} is not a query command.")
    return runtime.execute_query_command(agent_name, invocation.command_name, timeout)


def execute_action(runtime, agent_name, message, timeout=60):
    invocation = parse_command_message(message)
    if invocation.command_name not in {"!stop", "!goal", "!newAction"}:
        raise ValueError(f"{invocation.command_name} is not a action command.")
    return runtime.execute_action_command(agent_name, message, timeout)
