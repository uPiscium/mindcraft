from __future__ import annotations


class MemoryBank:
    def __init__(self):
        self.memory = {}

    def remember_place(self, name, x, y, z):
        self.memory[name] = [x, y, z]

    def recall_place(self, name):
        return self.memory.get(name)

    def get_json(self):
        return self.memory

    def load_json(self, json_data):
        self.memory = json_data or {}

    def get_keys(self):
        return ", ".join(self.memory.keys())
