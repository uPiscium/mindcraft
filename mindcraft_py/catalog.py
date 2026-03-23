import json
from math import inf
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


def _normalize_catalog_domains(catalog):
    normalized = []
    for command in catalog:
        command_copy = dict(command)
        params = command_copy.get("params")
        if params:
            params_copy = {}
            for param_name, param_data in params.items():
                param_copy = dict(param_data)
                if "domain" in param_copy and param_copy["domain"] is not None:
                    lower, upper, *rest = param_copy["domain"]
                    if upper == float("inf") or upper == inf:
                        upper = None
                    param_copy["domain"] = [lower, upper, *(rest[:1] or ["[)"])]
                params_copy[param_name] = param_copy
            command_copy["params"] = params_copy
        normalized.append(command_copy)
    return normalized


def _json_safe(value):
    if value == inf or value == float("inf"):
        return None
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def write_command_catalog(path=CATALOG_PATH):
    catalog = _json_safe(_normalize_catalog_domains(build_command_catalog()))
    path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def load_command_catalog(path=CATALOG_PATH):
    return json.loads(path.read_text(encoding="utf-8"))
