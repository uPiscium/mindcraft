from mindcraft_py.models.ollama import Ollama


class StubOllama(Ollama):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent_bodies = []

    def send(self, endpoint, body):
        self.sent_bodies.append({"endpoint": endpoint, "body": body})
        return {"message": {"content": "hello <think>skip</think> world"}}


def test_send_uses_requests_and_certifi(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "ok"}}

    def fake_post(url, json=None, timeout=None, verify=None):
        captured.update(
            {"url": url, "json": json, "timeout": timeout, "verify": verify}
        )
        return FakeResponse()

    monkeypatch.setattr("mindcraft_py.models.ollama.requests.post", fake_post)
    client = Ollama("test-model", "https://ollama-melchior.arc.upiscium.dev")

    result = client.send("/api/chat", {"model": "test-model"})

    assert result == {"message": {"content": "ok"}}
    assert captured["url"].startswith("https://ollama-melchior.arc.upiscium.dev")
    assert captured["timeout"] == 300
    assert captured["verify"] is not False


def test_send_request_strips_think_blocks():
    client = StubOllama(
        "test-model", "https://ollama-melchior.arc.upiscium.dev", {"temperature": 0.2}
    )

    result = client.send_request([{"role": "user", "content": "hi"}], "system")

    assert result == "hello  world"
    assert len(client.sent_bodies) == 1
    assert client.sent_bodies[0]["body"]["options"]["num_ctx"] == 4096
    assert client.sent_bodies[0]["body"]["temperature"] == 0.2


def test_strip_think_blocks_returns_none_for_partial_think():
    client = Ollama("test-model")

    assert client.strip_think_blocks("before <think>unfinished") is None
    assert (
        client.strip_think_blocks("before <think>done</think> after") == "before  after"
    )
