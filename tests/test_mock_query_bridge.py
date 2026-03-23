import socket
from pathlib import Path

from mindcraft_py.commands import execute_query
from mindcraft_py.profiles import load_profile
from mindcraft_py.runtime import MindcraftRuntime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_PROFILE_PATH = PROJECT_ROOT / "agents" / "Andy.toml"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_mock_query_bridge_runs_without_minecraft():
    runtime = MindcraftRuntime()
    port = find_free_port()

    try:
        runtime.init(
            port=port,
            host_public=False,
            auto_open_ui=False,
            startup_timeout=20,
        )

        settings = {
            "host": "127.0.0.1",
            "port": 25565,
            "auth": "offline",
            "mock_client": True,
            "blocked_actions": [],
        }
        settings["profile"] = load_profile(AGENT_PROFILE_PATH)
        runtime.create_agent(settings, timeout=20)

        result = execute_query(
            runtime, settings["profile"]["name"], "!stats", timeout=20
        )

        assert "STATS" in result
        assert "- Health: 20 / 20" in result
    finally:
        runtime.shutdown()


def test_mock_query_bridge_supports_more_queries_without_minecraft():
    runtime = MindcraftRuntime()
    port = find_free_port()

    try:
        runtime.init(
            port=port,
            host_public=False,
            auto_open_ui=False,
            startup_timeout=20,
        )

        settings = {
            "host": "127.0.0.1",
            "port": 25565,
            "auth": "offline",
            "mock_client": True,
            "blocked_actions": [],
        }
        settings["profile"] = load_profile(AGENT_PROFILE_PATH)
        runtime.create_agent(settings, timeout=20)

        craftable = execute_query(runtime, settings["profile"]["name"], "!craftable")
        help_text = execute_query(runtime, settings["profile"]["name"], "!help")

        assert "CRAFTABLE_ITEMS" in craftable
        assert "Mock help" in help_text or "available" in help_text
    finally:
        runtime.shutdown()
