from __future__ import annotations

import json
import re
from pathlib import Path

_ERROR_DEFINITIONS_PATH = Path(__file__).with_name("connection_errors.json")

with _ERROR_DEFINITIONS_PATH.open("r", encoding="utf-8") as fh:
    ERROR_DEFINITIONS = json.load(fh)


def log(agent_name, msg):
    print(msg)


def parse_kick_reason(reason):
    if not reason:
        return {"type": "unknown", "msg": "Unknown reason (Empty)", "isFatal": True}

    raw = (reason if isinstance(reason, str) else json.dumps(reason)).lower()

    for type_name, definition in ERROR_DEFINITIONS.items():
        if any(keyword in raw for keyword in definition["keywords"]):
            return {
                "type": type_name,
                "msg": definition["msg"],
                "isFatal": definition["isFatal"],
            }

    fallback = raw
    try:
        obj = reason if isinstance(reason, dict) else json.loads(reason)
        fallback = (
            obj.get("translate")
            or obj.get("text")
            or obj.get("value", {}).get("translate")
            or raw
        )
    except Exception:
        pass

    return {"type": "other", "msg": f"Disconnected: {fallback}", "isFatal": True}


def handle_disconnection(agent_name, reason):
    parsed = parse_kick_reason(reason)
    final_msg = f"[LoginGuard] {parsed['msg']}"
    log(agent_name, final_msg)
    return {"type": parsed["type"], "msg": final_msg}


def validate_name_format(name):
    if not name or not re.match(r"^[a-zA-Z0-9_]{3,16}$", name):
        return {
            "success": False,
            "msg": (
                f"[LoginGuard] Invalid name '{name}'. Must be 3-16 "
                "alphanumeric/underscore characters."
            ),
        }
    return {"success": True}
