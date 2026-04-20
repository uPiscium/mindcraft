from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mindcraft_py.runtime import MindcraftRuntime


@dataclass
class TaskExecutionPlan:
    task_id: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    current_step_index: int = 0

    def has_next(self) -> bool:
        return self.current_step_index < len(self.steps)

    def next_step(self) -> dict[str, Any] | None:
        if not self.has_next():
            return None
        step = self.steps[self.current_step_index]
        self.current_step_index += 1
        return step


class TaskExecutor:
    def plan(self, task: dict[str, Any]) -> TaskExecutionPlan:
        payload = str(task.get("payload") or task.get("goal") or "").strip()
        steps = [{"type": "natural_language", "content": payload}] if payload else []
        return TaskExecutionPlan(task_id=str(task["id"]), steps=steps)

    def execute_step(self, step: dict[str, Any]) -> dict[str, Any]:
        if not step:
            return {"success": False, "reason": "empty step"}
        if step.get("type") == "natural_language":
            content = str(step.get("content", "")).strip()
            if not content:
                return {"success": False, "reason": "empty task payload"}
            return {"success": True, "reason": content}
        return {
            "success": False,
            "reason": f"unsupported step type: {step.get('type')}",
        }


@dataclass
class TaskExecutionResult:
    success: bool
    reason: str
    steps: list[dict[str, Any]] = field(default_factory=list)


class TaskExecutionController:
    def __init__(self, runtime: MindcraftRuntime, executor: TaskExecutor | None = None):
        self.runtime = runtime
        self.executor = executor or TaskExecutor()

    def run(self, requester_id: str, task_id: str) -> TaskExecutionResult:
        task = self.runtime.acquire_task_by_id(requester_id, task_id)
        plan = self.executor.plan(task)
        executed_steps: list[dict[str, Any]] = []

        while plan.has_next():
            step = plan.next_step()
            if step is None:
                break
            step_result = self.executor.execute_step(step)
            executed_steps.append({"step": step, "result": step_result})

            if not step_result.get("success", False):
                self.runtime.yield_task(
                    requester_id, task_id, step_result.get("reason", "task failed")
                )
                return TaskExecutionResult(
                    success=False,
                    reason=str(step_result.get("reason", "task failed")),
                    steps=executed_steps,
                )

        reason = f"task {task_id} completed"
        self.runtime.complete_task(requester_id, task_id, reason)
        return TaskExecutionResult(success=True, reason=reason, steps=executed_steps)
