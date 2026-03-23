import argparse
import json
import os
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 unsupported anyway
    tomllib = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS_TOML_PATH = PROJECT_ROOT / "settings.toml"
DEFAULT_SETTINGS_PATH = PROJECT_ROOT / "settings.js"


def _strip_js_line_comments(content):
    result = []
    in_string = None
    escape_next = False
    index = 0

    while index < len(content):
        char = content[index]
        next_char = content[index + 1] if index + 1 < len(content) else ""

        if in_string:
            result.append(char)
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == in_string:
                in_string = None
            index += 1
            continue

        if char in {'"', "'"}:
            in_string = char
            result.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            while index < len(content) and content[index] != "\n":
                index += 1
            continue

        result.append(char)
        index += 1

    return "".join(result)


def _extract_settings_object(content):
    markers = ["const settings", "export default"]
    start = -1
    for marker in markers:
        marker_index = content.find(marker)
        if marker_index != -1:
            start = content.find("{", marker_index)
            if start != -1:
                break

    if start == -1:
        raise RuntimeError("Could not locate settings object in settings source")

    depth = 0
    in_string = None
    escape_next = False

    for index in range(start, len(content)):
        char = content[index]
        if in_string:
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == in_string:
                in_string = None
            continue

        if char in {'"', "'"}:
            in_string = char
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[start : index + 1]

    raise RuntimeError("Could not parse settings object from settings source")


def _load_base_settings(settings_path=DEFAULT_SETTINGS_PATH):
    toml_path = DEFAULT_SETTINGS_TOML_PATH
    if tomllib is not None and toml_path.exists():
        with open(toml_path, "rb") as file_obj:
            return tomllib.load(file_obj)

    with open(settings_path, "r", encoding="utf-8") as file_obj:
        content = file_obj.read()

    sanitized = _strip_js_line_comments(content)
    object_literal = _extract_settings_object(sanitized)
    object_literal = object_literal.replace("'", '"')
    object_literal = re.sub(r",(\s*[}\]])", r"\1", object_literal)

    try:
        return json.loads(object_literal)
    except json.JSONDecodeError as error:
        raise RuntimeError("Failed to parse settings from settings.js") from error


def _parse_bool(value):
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _coerce_value(current_value, new_value):
    if isinstance(current_value, bool):
        return _parse_bool(new_value)
    if isinstance(current_value, int) and not isinstance(current_value, bool):
        return int(new_value)
    return new_value


def _parse_cli_args(cli_args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", nargs="+", help="List of agent profile paths")
    parser.add_argument("--task_path", help="Path to task file to execute")
    parser.add_argument("--task_id", help="Task ID to execute")
    args, _ = parser.parse_known_args(cli_args)
    return args


def _apply_settings_json_override(settings, env):
    settings_json = env.get("SETTINGS_JSON")
    if not settings_json:
        return

    try:
        override = json.loads(settings_json)
    except json.JSONDecodeError as error:
        raise RuntimeError("Failed to parse SETTINGS_JSON") from error

    if not isinstance(override, dict):
        raise RuntimeError("SETTINGS_JSON must decode to an object")

    settings.update(override)


def _apply_cli_overrides(settings, cli_args):
    args = _parse_cli_args(cli_args)

    if args.profiles:
        settings["profiles"] = args.profiles

    if args.task_path:
        with open(args.task_path, "r", encoding="utf-8") as file_obj:
            tasks = json.load(file_obj)

        if not args.task_id:
            raise RuntimeError("task_id is required when task_path is provided")

        settings["task"] = tasks[args.task_id]
        settings["task"]["task_id"] = args.task_id


def _apply_env_overrides(settings, env):
    scalar_overrides = {
        "MINECRAFT_PORT": "port",
        "MINDSERVER_PORT": "mindserver_port",
        "MAX_MESSAGES": "max_messages",
        "NUM_EXAMPLES": "num_examples",
        "LOG_ALL": "log_all_prompts",
    }

    for env_key, settings_key in scalar_overrides.items():
        if env_key in env:
            settings[settings_key] = _coerce_value(
                settings.get(settings_key), env[env_key]
            )

    if env.get("PROFILES"):
        profiles = json.loads(env["PROFILES"])
        if profiles:
            settings["profiles"] = profiles

    if env.get("INSECURE_CODING") is not None:
        settings["allow_insecure_coding"] = _parse_bool(env["INSECURE_CODING"])

    if env.get("BLOCKED_ACTIONS"):
        settings["blocked_actions"] = json.loads(env["BLOCKED_ACTIONS"])


def resolve_settings(cli_args=None, env=None):
    if cli_args is None:
        cli_args = []
    if env is None:
        env = os.environ.copy()

    settings = _load_base_settings()
    _apply_settings_json_override(settings, env)
    _apply_cli_overrides(settings, cli_args)
    _apply_env_overrides(settings, env)
    return settings
