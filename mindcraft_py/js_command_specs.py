from __future__ import annotations

from mindcraft_py.commands import get_default_command_specs


def extract_js_command_specs(command_names):
    specs = {}
    for command in get_default_command_specs():
        if command.name in command_names:
            specs[command.name] = command
    return specs
