from __future__ import annotations

from typing import Any

from mindcraft_py.runtime import MindcraftRuntime
from mindcraft_py.task_execution_controller import TaskExecutionController
from mindcraft_py.task_slot import EMPTY, RUNNING


class TaskOrchestrator:
    def __init__(self, runtime: MindcraftRuntime):
        self.runtime = runtime
        self.controller = TaskExecutionController(runtime)

    def tick(self, agent_name: str) -> dict[str, Any]:
        slot = self.runtime.get_task_slot(agent_name)
        if slot.is_empty():
            return {"status": EMPTY, "task": None}

        if slot.state == RUNNING:
            return self._run_slot(agent_name)

        if slot.state == "ASSIGNED":
            slot.mark_running()
            return self._run_slot(agent_name)

        return {"status": slot.state, "task": slot.task}

    def _run_slot(self, agent_name: str) -> dict[str, Any]:
        slot = self.runtime.get_task_slot(agent_name)
        task = slot.task
        if not task:
            return {"status": EMPTY, "task": None}

        slot.mark_running()
        result = self.controller.run_assigned(agent_name)
        if result is None:
            self.runtime.clear_task_slot(agent_name)
            return {"status": EMPTY, "task": None}
        if result.success:
            self.runtime.clear_task_slot(agent_name)
            return {"status": "COMPLETED", "task": task, "result": result}

        self.runtime.clear_task_slot(agent_name)
        return {"status": "FAILED", "task": task, "result": result}
