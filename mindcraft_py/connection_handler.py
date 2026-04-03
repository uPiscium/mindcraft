from __future__ import annotations

import json
import re


ERROR_DEFINITIONS = {
    "name_conflict": {
        "keywords": [
            "name_taken",
            "duplicate_login",
            "already connected",
            "already logged in",
            "username is already",
        ],
        "msg": "Name Conflict: The name is already in use or you are already logged in.",
        "isFatal": True,
    },
    "access_denied": {
        "keywords": ["whitelist", "not white-listed", "banned", "suspended", "verify"],
        "msg": "Access Denied: You are not whitelisted or banned.",
        "isFatal": True,
    },
    "server_full": {
        "keywords": ["server is full", "full server"],
        "msg": "Connection Failed: The server is full.",
        "isFatal": False,
    },
    "version_mismatch": {
        "keywords": ["outdated", "version", "client"],
        "msg": "Version Mismatch: Client and server versions do not match.",
        "isFatal": True,
    },
    "maintenance": {
        "keywords": ["maintenance", "updating", "closed", "restarting"],
        "msg": "Connection Failed: Server is under maintenance or restarting.",
        "isFatal": False,
    },
    "network_error": {
        "keywords": [
            "timeout",
            "timed out",
            "connection lost",
            "reset",
            "refused",
            "keepalive",
        ],
        "msg": "Network Error: Connection timed out or was lost.",
        "isFatal": False,
    },
    "behavior": {
        "keywords": ["flying", "spam", "speed"],
        "msg": "Kicked: Removed from server due to flying, spamming, or invalid movement.",
        "isFatal": True,
    },
}


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
            "msg": f"[LoginGuard] Invalid name '{name}'. Must be 3-16 alphanumeric/underscore characters.",
        }
    return {"success": True}
