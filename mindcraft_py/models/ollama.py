from __future__ import annotations

import base64
import re

import requests

from mindcraft_py.utils.text import strict_format


class Ollama:
    prefix = "ollama"

    def __init__(self, model_name, url=None, params=None):
        self.model_name = model_name
        self.params = params or {}
        self.url = url or "https://ollama-melchior.arc.upiscium.dev"
        self.chat_endpoint = "/api/chat"
        self.embedding_endpoint = "/api/embeddings"

    def send_request(self, turns, system_message):
        model = self.model_name or "sweaterdog/andy-4:q8_0"
        messages = strict_format(turns)
        messages.insert(0, {"role": "system", "content": system_message})
        max_attempts = 5
        ollama_options = {"num_ctx": 4096}
        attempt = 0
        final_res = None

        while attempt < max_attempts:
            attempt += 1
            print(f"Awaiting local response... (model: {model}, attempt: {attempt})")
            res = None
            try:
                api_response = self.send(
                    self.chat_endpoint,
                    {
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "options": ollama_options,
                        **self.params,
                    },
                )
                if api_response:
                    res = api_response["message"]["content"]
                else:
                    res = "No response data."
            except Exception as err:
                error_text = str(getattr(err, "message", err)).lower()
                if "504" in error_text or "timeout" in error_text:
                    print("Ollama request timed out or returned 504.")
                else:
                    print(err)
                    res = "My brain disconnected, try again."

            cleaned_res = self.strip_think_blocks(res)
            if cleaned_res is None:
                print("Partial <think> block detected. Re-generating...")
                if attempt < max_attempts:
                    continue
                res_text = "I thought too hard, sorry, try again."
            else:
                res_text = cleaned_res

            final_res = res_text
            break

        if final_res is None:
            print("Could not get a valid response after max attempts.")
            final_res = "I thought too hard, sorry, try again."
        return final_res

    def embed(self, text):
        model = self.model_name or "embeddinggemma:latest"
        body = {"model": model, "input": text}
        res = self.send(self.embedding_endpoint, body)
        return res["embedding"]

    def send_vision_request(self, messages, system_message, image_buffer):
        image_messages = list(messages)
        image_data = ""
        if isinstance(image_buffer, (bytes, bytearray)):
            image_data = base64.b64encode(image_buffer).decode("ascii")
        image_messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + image_data,
                        },
                    },
                ],
            }
        )
        return self.send_request(image_messages, system_message)

    def strip_think_blocks(self, content):
        if content is None:
            return ""
        text = str(content)
        open_count = text.count("<think>")
        close_count = text.count("</think>")
        if open_count > close_count:
            return None
        return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

    def send(self, endpoint, body):
        url = self.url.rstrip("/") + endpoint
        try:
            response = requests.post(url, json=body, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.Timeout as err:
            raise RuntimeError(
                "Request to Ollama timed out (5 minutes limit)."
            ) from err
        except requests.RequestException as err:
            print("Failed to send Ollama request.")
            print(err)
            raise

    # JS-style aliases
    sendRequest = send_request
    sendVisionRequest = send_vision_request
