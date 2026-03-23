import ast
import re
from pathlib import Path

from .commands import CommandParam, CommandSpec

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMAND_FILES = (
    PROJECT_ROOT / "src" / "agent" / "commands" / "queries.js",
    PROJECT_ROOT / "src" / "agent" / "commands" / "actions.js",
)

ARRAY_MARKERS = {
    "queries.js": "export const queryList = [",
    "actions.js": "export const actionsList = [",
}

FIELD_REGEXES = {
    "name": re.compile(r'name\s*:\s*(?P<value>"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\')'),
    "description": re.compile(
        r'description\s*:\s*(?P<value>"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\')'
    ),
    "type": re.compile(r'type\s*:\s*(?P<value>"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\')'),
}


def extract_js_command_specs(command_names=None):
    requested = set(command_names or [])
    specs = {}

    for command_file in COMMAND_FILES:
        for command_text in _extract_command_objects(command_file):
            spec = _parse_command_spec(command_text, command_file.name)
            if requested and spec.name not in requested:
                continue
            specs[spec.name] = spec

    return specs


def _extract_command_objects(command_file):
    source = command_file.read_text(encoding="utf-8")
    marker = ARRAY_MARKERS[command_file.name]
    start = source.find(marker)
    if start == -1:
        raise RuntimeError(f"Could not find command list marker in {command_file}")

    array_start = source.find("[", start)
    array_end = _find_matching_delimiter(source, array_start, "[", "]")
    array_content = source[array_start + 1 : array_end]
    return _extract_top_level_objects(array_content)


def _extract_top_level_objects(source):
    objects = []
    index = 0
    start = None
    depth = 0
    state = _ScannerState()

    while index < len(source):
        next_index, char = state.consume(source, index)
        if char is None:
            index = next_index + 1
            continue

        if char == "{":
            if depth == 0:
                start = next_index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objects.append(source[start : next_index + 1])
                start = None

        index = next_index + 1

    return objects


def _parse_command_spec(command_text, filename):
    kind = "query" if filename == "queries.js" else "action"
    name = _extract_string_field("name", command_text)
    description = _extract_string_field("description", command_text)
    params_text = _extract_object_field("params", command_text)
    params = None
    if params_text is not None:
        params = _parse_params(params_text)

    return CommandSpec(name=name, description=description, params=params, kind=kind)


def _parse_params(params_text):
    params = {}
    inner = params_text[1:-1]
    index = 0

    while index < len(inner):
        index = _skip_whitespace_and_commas(inner, index)
        if index >= len(inner):
            break

        key_match = re.match(
            r'(?P<quote>["\'])?(?P<key>\w+)(?(quote)(?P=quote))\s*:',
            inner[index:],
        )
        if not key_match:
            raise RuntimeError("Failed to parse params block from JavaScript source")

        key = key_match.group("key")
        index += key_match.end()
        index = _skip_whitespace(inner, index)
        if index >= len(inner) or inner[index] != "{":
            raise RuntimeError("Expected object literal for command parameter")

        param_end = _find_matching_delimiter(inner, index, "{", "}")
        param_text = inner[index : param_end + 1]
        params[key] = CommandParam(
            type=_extract_string_field("type", param_text),
            description=_extract_string_field("description", param_text),
        )
        index = param_end + 1

    return params


def _extract_string_field(field_name, source):
    match = FIELD_REGEXES[field_name].search(source)
    if not match:
        raise RuntimeError(f"Could not parse {field_name} from JavaScript source")
    return ast.literal_eval(match.group("value"))


def _extract_object_field(field_name, source):
    match = re.search(rf"{field_name}\s*:\s*{{", source)
    if not match:
        return None

    start = source.find("{", match.start())
    end = _find_matching_delimiter(source, start, "{", "}")
    return source[start : end + 1]


def _find_matching_delimiter(source, start, open_char, close_char):
    depth = 0
    index = start
    state = _ScannerState()

    while index < len(source):
        next_index, char = state.consume(source, index)
        if char is None:
            index = next_index + 1
            continue

        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return next_index

        index = next_index + 1

    raise RuntimeError(f"Could not find matching {close_char!r} in JavaScript source")


def _skip_whitespace(source, index):
    while index < len(source) and source[index].isspace():
        index += 1
    return index


def _skip_whitespace_and_commas(source, index):
    while index < len(source) and (source[index].isspace() or source[index] == ","):
        index += 1
    return index


class _ScannerState:
    def __init__(self):
        self.string_delimiter = None
        self.escape_next = False
        self.in_line_comment = False
        self.in_block_comment = False

    def consume(self, source, index):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""

        if self.in_line_comment:
            if char == "\n":
                self.in_line_comment = False
                return index, char
            return index, None

        if self.in_block_comment:
            if char == "*" and next_char == "/":
                self.in_block_comment = False
                return index + 1, None
            return index, None

        if self.string_delimiter is not None:
            if self.escape_next:
                self.escape_next = False
            elif char == "\\":
                self.escape_next = True
            elif char == self.string_delimiter:
                self.string_delimiter = None
            return index, None

        if char == "/" and next_char == "/":
            self.in_line_comment = True
            return index + 1, None

        if char == "/" and next_char == "*":
            self.in_block_comment = True
            return index + 1, None

        if char in {'"', "'"}:
            self.string_delimiter = char
            return index, None

        return index, char
