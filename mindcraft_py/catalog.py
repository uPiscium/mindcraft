from __future__ import annotations

from mindcraft_py.commands import get_default_command_specs


def load_command_catalog():
    return build_command_catalog()


def build_command_catalog():
    catalog = []
    for command in get_default_command_specs():
        catalog.append(
            {
                "name": command.name,
                "description": command.description,
                "kind": command.kind,
                "params": {
                    name: {
                        "type": param.type,
                        "description": param.description,
                        **({"domain": param.domain} if param.domain else {}),
                    }
                    for name, param in (command.params or {}).items()
                },
            }
        )
    return catalog
