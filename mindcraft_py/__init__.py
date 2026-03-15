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


def shutdown():
    _default_runtime.shutdown()


def wait():
    _default_runtime.wait()


def get_runtime():
    return _default_runtime
