from __future__ import annotations

import json
import re
from typing import Any

import requests


class ConstrainedDecoderError(RuntimeError):
    pass


class ConstrainedDecoderGateway:
    def __init__(
        self,
        url: str = "http://0.0.0.0:8000/v1",
        model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        api_key: str = "",
        max_attempts: int = 3,
        timeout: int = 300,
    ):
        self.url = url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.timeout = timeout

    def generate_action(self, prompt: str, schema_definition: dict[str, Any]) -> Any:
        attempt_prompt = prompt
        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            payload = self._build_payload(attempt_prompt, schema_definition)
            response = self._post_json("/chat/completions", payload)
            content = self._extract_content(response)

            try:
                return self._parse_content(content)
            except (json.JSONDecodeError, ValueError, TypeError) as err:
                last_error = err
                if attempt >= self.max_attempts:
                    break
                attempt_prompt = (
                    prompt
                    + "\n\nPrevious output was invalid JSON. "
                    + f"Error: {err}. Return only valid JSON matching the schema."
                )

        raise ConstrainedDecoderError(
            str(last_error) if last_error else "Unknown parse error."
        )

    def _build_payload(
        self, prompt: str, schema_definition: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "generated_action",
                    "schema": schema_definition,
                    "strict": True,
                },
            },
        }

    def _post_json(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = requests.post(
            self.url + endpoint,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _extract_content(self, response: dict[str, Any]) -> Any:
        if isinstance(response, dict):
            choices = response.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                if "content" in message:
                    return message["content"]
            if "content" in response:
                return response["content"]
        return response

    def _parse_content(self, content: Any) -> Any:
        if isinstance(content, (dict, list)):
            return content
        text = str(content).strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
        return json.loads(text)


GenerateAction = ConstrainedDecoderGateway.generate_action
