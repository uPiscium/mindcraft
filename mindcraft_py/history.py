from __future__ import annotations

import json
from pathlib import Path


class History:
    def __init__(self, name, base_dir="./bots"):
        self.name = name
        self.base_dir = Path(base_dir)
        self.memory_fp = self.base_dir / name / "memory.json"
        self.full_history_fp = None
        self.turns = []
        self.memory = ""

    def get_history(self):
        return json.loads(json.dumps(self.turns))

    def append_full_history(self, to_store):
        histories_dir = self.base_dir / self.name / "histories"
        histories_dir.mkdir(parents=True, exist_ok=True)
        if self.full_history_fp is None:
            self.full_history_fp = histories_dir / "full_history.json"
            self.full_history_fp.write_text("[]", encoding="utf-8")
        data = json.loads(self.full_history_fp.read_text(encoding="utf-8"))
        data.extend(to_store)
        self.full_history_fp.write_text(json.dumps(data, indent=4), encoding="utf-8")

    def save(
        self,
        self_prompting_state=None,
        self_prompt=None,
        task_start=None,
        last_sender=None,
    ):
        self.memory_fp.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "memory": self.memory,
            "turns": self.turns,
            "self_prompting_state": self_prompting_state,
            "self_prompt": self_prompt,
            "taskStart": task_start,
            "last_sender": last_sender,
        }
        self.memory_fp.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self):
        if not self.memory_fp.exists():
            return None
        data = json.loads(self.memory_fp.read_text(encoding="utf-8"))
        self.memory = data.get("memory", "")
        self.turns = data.get("turns", [])
        return data

    def clear(self):
        self.turns = []
        self.memory = ""
