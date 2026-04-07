from mindcraft_py.agent_process import AgentProcess


class FakeNodeRuntime:
    def __init__(self):
        self.calls = []

    def start(self, profiles=None, task_path=None, task_id=None):
        self.calls.append(("start", profiles, task_path, task_id))
        return object()

    def stop(self):
        self.calls.append(("stop",))


def test_agent_process_start_and_stop():
    node_runtime = FakeNodeRuntime()
    process = AgentProcess("Andy", node_runtime)

    process.start(profile_path="./agents/Andy.toml")
    process.stop()

    assert node_runtime.calls[0] == ("start", ["./agents/Andy.toml"], None, None)
    assert node_runtime.calls[1] == ("stop",)


def test_agent_process_handle_exit_does_not_restart_too_fast():
    node_runtime = FakeNodeRuntime()
    process = AgentProcess("Andy", node_runtime)
    process.start(profile_path="./agents/Andy.toml")

    restarted = process.handle_exit(code=1, signal=None)

    assert restarted is False


def test_agent_process_handle_exit_restarts_after_delay(monkeypatch):
    node_runtime = FakeNodeRuntime()
    process = AgentProcess("Andy", node_runtime)
    process.start(profile_path="./agents/Andy.toml")
    process.last_restart -= 11

    restarted = process.handle_exit(code=1, signal=None)

    assert restarted is True
