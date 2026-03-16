import re
from dataclasses import dataclass
from functools import lru_cache

TYPE_TRANSLATIONS = {
    "float": "number",
    "int": "number",
    "boolean": "bool",
    "string": "string",
}

COMMAND_REGEX = re.compile(
    r'!(\w+)(?:\(((?:-?\d+(?:\.\d+)?|true|false|"[^"]*")(?:\s*,\s*(?:-?\d+(?:\.\d+)?|true|false|"[^"]*"))*)\))?'
)
ARG_REGEX = re.compile(r'-?\d+(?:\.\d+)?|true|false|"[^"]*"')


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
    bridge: str | None = None


@dataclass(frozen=True)
class CommandInvocation:
    command_name: str
    args: tuple


class PythonCommandRegistry:
    def __init__(self, commands=None):
        self._commands = {}
        if commands:
            for command in commands:
                self.register(command)

    def register(self, command):
        self._commands[command.name] = command

    def command_names(self):
        return tuple(self._commands.keys())

    def commands(self):
        return tuple(self._commands.values())

    def get(self, command_name):
        if not command_name.startswith("!"):
            command_name = f"!{command_name}"
        return self._commands.get(command_name)

    def contains(self, command_name):
        return self.get(command_name) is not None

    def parse_message(self, message):
        command_match = COMMAND_REGEX.search(message)
        if not command_match:
            raise ValueError("Command is incorrectly formatted")

        command_name = f"!{command_match.group(1)}"
        command = self.get(command_name)
        if command is None:
            raise ValueError(f"{command_name} is not a command.")

        raw_args = []
        if command_match.group(2):
            raw_args = ARG_REGEX.findall(command_match.group(2))

        params = list((command.params or {}).items())
        if len(raw_args) != len(params):
            raise ValueError(
                f"Command {command.name} was given {len(raw_args)} args, "
                f"but requires {len(params)} args."
            )

        parsed_args = []
        for index, ((param_name, param_spec), raw_arg) in enumerate(
            zip(params, raw_args, strict=True)
        ):
            try:
                parsed_arg = _coerce_argument(raw_arg, param_spec)
            except ValueError as error:
                raise ValueError(f"Error: Param '{param_name}' {error}") from error

            if isinstance(parsed_arg, (int, float)) and param_spec.domain is not None:
                if not _check_in_interval(parsed_arg, *param_spec.domain):
                    endpoint_type = (
                        param_spec.domain[2] if len(param_spec.domain) > 2 else "[)"
                    )
                    raise ValueError(
                        f"Error: Param '{param_name}' must be an element of "
                        f"{endpoint_type[0]}{param_spec.domain[0]}, "
                        f"{param_spec.domain[1]}{endpoint_type[1]}."
                    )

            parsed_args.append(parsed_arg)

        return CommandInvocation(command_name=command_name, args=tuple(parsed_args))

    def contains_command(self, message):
        command_match = COMMAND_REGEX.search(message)
        if command_match:
            return f"!{command_match.group(1)}"
        return None

    def trunc_command_message(self, message):
        command_match = COMMAND_REGEX.search(message)
        if command_match:
            return message[: command_match.end()]
        return message

    def get_command_docs(self, blocked_actions=None):
        blocked = set(blocked_actions or [])
        docs = [
            "",
            "*COMMAND DOCS",
            (
                " You can use the following commands to perform actions and get "
                "information about the world. "
            ),
            (
                "    Use the commands with the syntax: !commandName or "
                '!commandName("arg1", 1.2, ...) if the command takes arguments.'
            ),
            (
                "    Do not use codeblocks. Use double quotes for strings. "
                "Only use one command in each response, trailing commands and "
                "comments will be ignored."
            ),
        ]

        for command in self._commands.values():
            if command.name in blocked:
                continue
            docs.append(f"{command.name}: {command.description}")
            if command.params:
                docs.append("Params:")
                for param_name, param_spec in command.params.items():
                    translated_type = TYPE_TRANSLATIONS.get(
                        param_spec.type, param_spec.type
                    )
                    docs.append(
                        f"{param_name}: ({translated_type}) {param_spec.description}"
                    )

        docs.append("*")
        return "\n".join(docs)

    def execute_query(self, runtime, agent_name, message, timeout=60):
        invocation = self.parse_message(message)
        command = self.get(invocation.command_name)
        if command is None:
            raise ValueError(f"{invocation.command_name} is not a command.")
        if command.kind != "query":
            raise ValueError(f"{command.name} is not a query command.")
        if command.bridge != "js":
            raise ValueError(f"{command.name} does not have a JavaScript query bridge.")

        return runtime.execute_query_command(
            agent_name,
            self.trunc_command_message(message),
            timeout=timeout,
        )


def _parse_boolean(value):
    normalized = value.lower()
    if normalized in {"false", "f", "0", "off"}:
        return False
    if normalized in {"true", "t", "1", "on"}:
        return True
    raise ValueError("must be of type boolean.")


def _coerce_argument(raw_arg, param_spec):
    value = raw_arg.strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    if param_spec.type == "string":
        return value
    if param_spec.type == "int":
        try:
            return int(value)
        except ValueError as error:
            raise ValueError("must be of type int.") from error
    if param_spec.type == "float":
        try:
            return float(value)
        except ValueError as error:
            raise ValueError("must be of type float.") from error
    if param_spec.type == "boolean":
        return _parse_boolean(value)

    raise ValueError(f"has an unsupported Python command type: {param_spec.type}.")


def _check_in_interval(number, lower_bound, upper_bound, endpoint_type="[)"):
    if endpoint_type == "[)":
        return lower_bound <= number < upper_bound
    if endpoint_type == "()":
        return lower_bound < number < upper_bound
    if endpoint_type == "(]":
        return lower_bound < number <= upper_bound
    if endpoint_type == "[]":
        return lower_bound <= number <= upper_bound
    raise ValueError(f"Unknown endpoint type: {endpoint_type}")


def create_default_registry():
    return PythonCommandRegistry(
        commands=[
            CommandSpec(
                name="!stats",
                description="Get your bot's location, health, hunger, and time of day.",
                kind="query",
                bridge="js",
            ),
            CommandSpec(
                name="!inventory",
                description="Get your bot's inventory.",
                kind="query",
                bridge="js",
            ),
            CommandSpec(
                name="!nearbyBlocks",
                description="Get the blocks near the bot.",
                kind="query",
                bridge="js",
            ),
            CommandSpec(
                name="!entities",
                description="Get the nearby players and entities.",
                kind="query",
                bridge="js",
            ),
            CommandSpec(
                name="!newAction",
                description=(
                    "Perform new and unknown custom behaviors that are not "
                    "available as a command."
                ),
                params={
                    "prompt": CommandParam(
                        type="string",
                        description=(
                            "A natural language prompt to guide code generation. "
                            "Make a detailed step-by-step plan."
                        ),
                    )
                },
                kind="action",
            ),
            CommandSpec(
                name="!stop",
                description=(
                    "Force stop all actions and commands that are currently executing."
                ),
                kind="action",
            ),
            CommandSpec(
                name="!goal",
                description=(
                    "Set a goal prompt to endlessly work towards with "
                    "continuous self-prompting."
                ),
                params={
                    "selfPrompt": CommandParam(
                        type="string",
                        description="The goal prompt.",
                    )
                },
                kind="action",
            ),
        ]
    )


@lru_cache(maxsize=1)
def get_default_registry():
    return create_default_registry()


def get_command_docs(blocked_actions=None):
    return get_default_registry().get_command_docs(blocked_actions=blocked_actions)


def contains_command(message):
    return get_default_registry().contains_command(message)


def trunc_command_message(message):
    return get_default_registry().trunc_command_message(message)


def parse_command_message(message):
    return get_default_registry().parse_message(message)


def execute_query(runtime, agent_name, message, timeout=60):
    return get_default_registry().execute_query(
        runtime,
        agent_name,
        message,
        timeout=timeout,
    )
