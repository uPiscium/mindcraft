from __future__ import annotations

import json
from pathlib import Path


def _load_toml(path):
    import tomllib

    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_profile(path):
    path = Path(path)
    if path.suffix == ".toml":
        return _load_toml(path)
    raise ValueError(f"Unsupported profile format: {path.suffix}")
