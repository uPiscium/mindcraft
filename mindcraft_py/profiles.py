import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ provides tomllib
    tomllib = None


def load_profile(profile_path):
    path = Path(profile_path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    if suffix == ".toml":
        if tomllib is None:
            raise RuntimeError("TOML profile support requires Python 3.11+")

        with open(path, "rb") as file_obj:
            return tomllib.load(file_obj)

    raise ValueError(f"Unsupported profile format: {path.suffix}")
