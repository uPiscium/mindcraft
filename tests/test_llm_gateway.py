import pytest

from mindcraft_py.llm_gateway import ConstrainedDecoderError, ConstrainedDecoderGateway


def test_generate_action_includes_schema_and_retries_on_parse_error(monkeypatch):
    captured_payloads = []

    class FakeResponse:
        def __init__(self, content):
            self._content = content

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [{"message": {"content": self._content}}],
            }

    def fake_post(url, json=None, headers=None, timeout=None):
        captured_payloads.append(json)
        if len(captured_payloads) == 1:
            return FakeResponse("not json")
        return FakeResponse('{"action": "move"}')

    monkeypatch.setattr("mindcraft_py.llm_gateway.requests.post", fake_post)

    gateway = ConstrainedDecoderGateway(url="https://example.com", max_attempts=2)
    result = gateway.generate_action(
        "do something",
        {"type": "object", "properties": {"action": {"type": "string"}}},
    )

    assert result == {"action": "move"}
    assert captured_payloads[0]["response_format"]["json_schema"]["strict"] is True
    assert (
        "Previous output was invalid JSON"
        in captured_payloads[1]["messages"][0]["content"]
    )


def test_generate_action_raises_after_retries(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "still not json"}}]}

    monkeypatch.setattr(
        "mindcraft_py.llm_gateway.requests.post", lambda *a, **k: FakeResponse()
    )

    gateway = ConstrainedDecoderGateway(max_attempts=1)

    with pytest.raises(ConstrainedDecoderError):
        gateway.generate_action("prompt", {"type": "object"})
