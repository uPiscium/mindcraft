# ADR 0005: Task Pool BFS Runner

## Status

Accepted

## Context

The task pool already supports dependency-aware loading and runtime state transitions. What was missing was a concrete programmatic way to walk dependency chains in execution order so that the agent can process prerequisite tasks before dependent ones.

This is intended as a stepping stone toward a future self-directed task acquisition model.

## Decision

We will add a Python-side BFS-style runner that:

- computes a ready queue from task dependencies
- acquires tasks by dependency order
- executes a callback for each task
- completes or yields the task based on the callback result
- returns execution, completion, failure, and unresolved task lists

The runner is not the final autonomy model. It is an intermediate orchestration layer that can later be replaced by self-driven task selection while preserving the same task pool contract.

## Consequences

### Positive

- dependency chains can be exercised deterministically
- task progress is visible and testable from Python
- the current orchestration layer can be swapped out later without changing task file definitions

### Negative

- the runner is still an explicit orchestration step rather than autonomous behavior
- BFS ordering is an additional abstraction that is only useful while the system is still transitioning

### Neutral

- JS remains the execution boundary for Mineflayer-specific actions
- the runner only uses the existing Python runtime/task pool contract

## Related Files

- `mindcraft_py/task_runner.py`
- `mindcraft_py/runtime.py`
- `mindcraft_py/task_coordinator.py`
- `scripts/task_pool_bfs_demo.py`
- `tests/test_task_runner.py`
- `tasks/task_pool_demo.toml`
