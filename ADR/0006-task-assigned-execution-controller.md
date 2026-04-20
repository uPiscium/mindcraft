# ADR 0006: Task Execution Controller for Assigned Tasks

## Status

Accepted

## Context

The task pool can already load dependency-aware task files, and the BFS runner can execute dependency chains in order. What was still missing was a focused controller for the case where a task has already been assigned and needs to be executed to completion or yielded on failure.

This controller is meant to bridge the gap between task assignment and actual action execution.

## Decision

We will introduce a Python-side `TaskExecutionController` that owns the lifecycle of an assigned task.

The controller will:

- acquire a specific task by id
- build a simple execution plan from the task payload
- execute the plan step by step through a pluggable executor
- complete the task when execution succeeds
- yield the task when execution fails

The default executor treats the task payload as a natural-language instruction, which keeps the initial implementation simple while leaving room for task-specific planners later.

## Consequences

### Positive

- assigned tasks can be executed through a dedicated abstraction
- task execution becomes testable independently from task selection
- the controller provides a clean extension point for task-specific planners
- the runtime can keep BFS, self-directed acquisition, and assigned-task execution as separate concerns

### Negative

- the controller adds another orchestration layer
- the initial execution model is still coarse-grained and payload-driven
- the controller does not yet encode domain-specific Minecraft steps on its own

### Neutral

- BFS execution remains available for dependency-following runs
- JS remains the execution boundary for Mineflayer-specific actions

## Related Files

- `mindcraft_py/task_execution_controller.py`
- `mindcraft_py/task_runner.py`
- `mindcraft_py/runtime.py`
- `tests/test_task_execution_controller.py`
- `tests/test_task_runner.py`
