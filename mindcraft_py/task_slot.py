from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from time import time


EMPTY = "EMPTY"
ASSIGNED = "ASSIGNED"
RUNNING = "RUNNING"
COMPLETED = "COMPLETED"
FAILED = "FAILED"


@dataclass
class TaskSlot:
    state: str = EMPTY
    task: dict[str, Any] | None = None
    last_reason: str | None = None
    updated_at: float = field(default_factory=time)

    def is_empty(self) -> bool:
        return self.state == EMPTY or self.task is None

    def assign(self, task: dict[str, Any]) -> None:
        self.task = task
        self.state = ASSIGNED
        self.updated_at = time()
        self.last_reason = None

    def mark_running(self) -> None:
        if self.task is None:
            return
        self.state = RUNNING
        self.updated_at = time()

    def complete(self, reason: str | None = None) -> None:
        if self.task is None:
            return
        self.state = COMPLETED
        self.last_reason = reason
        self.updated_at = time()

    def fail(self, reason: str | None = None) -> None:
        if self.task is None:
            return
        self.state = FAILED
        self.last_reason = reason
        self.updated_at = time()

    def clear(self) -> None:
        self.state = EMPTY
        self.task = None
        self.last_reason = None
        self.updated_at = time()


class TaskSlotManager:
    def __init__(self):
        self._slots: dict[str, TaskSlot] = {}

    def get_slot(self, agent_name: str) -> TaskSlot:
        if agent_name not in self._slots:
            self._slots[agent_name] = TaskSlot()
        return self._slots[agent_name]

    def assign(self, agent_name: str, task: dict[str, Any]) -> TaskSlot:
        slot = self.get_slot(agent_name)
        slot.assign(task)
        return slot

    def mark_running(self, agent_name: str) -> TaskSlot:
        slot = self.get_slot(agent_name)
        slot.mark_running()
        return slot

    def complete(self, agent_name: str, reason: str | None = None) -> TaskSlot:
        slot = self.get_slot(agent_name)
        slot.complete(reason)
        return slot

    def fail(self, agent_name: str, reason: str | None = None) -> TaskSlot:
        slot = self.get_slot(agent_name)
        slot.fail(reason)
        return slot

    def clear(self, agent_name: str) -> TaskSlot:
        slot = self.get_slot(agent_name)
        slot.clear()
        return slot
