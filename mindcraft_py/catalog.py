import json
from pathlib import Path

from .commands import get_default_registry

CATALOG_PATH = Path(__file__).resolve().parent / "command_catalog.json"


def build_command_catalog():
    catalog = []
    for command in get_default_registry().commands():
        params = None
        if command.params:
            params = {}
            for param_name, param_spec in command.params.items():
                param_data = {
                    "type": param_spec.type,
                    "description": param_spec.description,
                }
                if param_spec.domain is not None:
                    param_data["domain"] = list(param_spec.domain)
                params[param_name] = param_data

        catalog.append(
            {
                "name": command.name,
                "description": command.description,
                "kind": command.kind,
                "bridge": command.bridge,
                "params": params,
            }
        )

    return catalog


def write_command_catalog(path=CATALOG_PATH):
    catalog = build_command_catalog()
    path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def load_command_catalog(path=CATALOG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))
