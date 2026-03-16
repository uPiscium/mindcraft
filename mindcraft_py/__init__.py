from .commands import (
    execute_query,
    get_command_docs,
    get_default_registry,
    parse_command_message,
)
from .runtime import MindcraftRuntime

_default_runtime = MindcraftRuntime()


def init(port=8080, host_public=True, auto_open_ui=True, startup_timeout=20):
    _default_runtime.init(
        port=port,
        host_public=host_public,
        auto_open_ui=auto_open_ui,
        startup_timeout=startup_timeout,
    )


def create_agent(settings_json, timeout=60):
    return _default_runtime.create_agent(settings_json, timeout=timeout)


def execute_query_command(agent_name, message, timeout=60):
    return execute_query(_default_runtime, agent_name, message, timeout=timeout)


def shutdown():
    _default_runtime.shutdown()


def wait():
    _default_runtime.wait()


def get_runtime():
    return _default_runtime


__all__ = [
    "MindcraftRuntime",
    "create_agent",
    "execute_query",
    "execute_query_command",
    "get_command_docs",
    "get_default_registry",
    "get_runtime",
    "init",
    "parse_command_message",
    "shutdown",
    "wait",
]
