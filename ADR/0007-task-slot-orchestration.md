# ADR 0007: Task Slot Orchestration

## Status

Accepted

## Context

The system now has a dependency-aware task pool, a BFS runner, and a controller for executing assigned tasks. What was still missing was a stable place inside each agent to hold the currently assigned task while the execution controller runs.

This missing layer is useful because it separates:

- task selection from task execution
- task execution from agent lifecycle management
- immediate assignment from eventual self-directed task acquisition

## Decision

We will introduce an explicit per-agent task slot as the handoff point between task assignment and task execution.

The chosen model is:

- task pool supplies tasks
- task slot stores the current task for an agent
- task execution controller operates on the slot contents
- the orchestrator decides whether the slot should be filled or executed

The slot state is intentionally explicit: `EMPTY`, `ASSIGNED`, `RUNNING`, `COMPLETED`, `FAILED`.

## Consequences

### Positive

- the system can track the current task independently from the selection logic
- controller execution becomes guard-railed by slot state
- stop / disconnect / shutdown can recover assigned work consistently
- future self-directed task acquisition can reuse the same slot contract

### Negative

- another orchestration layer is added
- task state is duplicated between the coordinator, runtime, and slot metadata
- the slot model must be kept in sync with lifecycle cleanup paths

### Neutral

- BFS runner remains available for dependency-following execution
- the task execution controller still handles the actual acquire / plan / execute / complete / yield sequence

## Related Files

- `mindcraft_py/task_slot.py`
- `mindcraft_py/task_slot_orchestrator.py`
- `mindcraft_py/task_execution_controller.py`
- `mindcraft_py/runtime.py`
- `tests/test_task_slot_orchestration.py`
