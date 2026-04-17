# ADR 0004: Python-Owned Task Pool Loading Boundary

## Status

Accepted

## Context

The task pool started as a mixed Python/JS implementation. Python owned the coordinator and file loader, while JS also contained a local task pool representation to support the live Mineflayer loop.

This split made it harder to keep task definition, dependency resolution, and lifecycle state consistent. The runtime boundary needs to be clearer: Python should own task loading and state transitions, while JS should only consume the task snapshot and drive the Minecraft execution loop.

## Decision

We will make Python the source of truth for task pool loading and task lifecycle data.

The chosen boundary is:

- Python loads the TOML task pool file and validates task definitions
- Python serializes the task pool into `TASK_POOL_JSON` for the Node runtime
- JS receives the task snapshot and uses it as runtime state only
- JS keeps the Mineflayer loop, self-prompting, and action execution

## Consequences

### Positive

- task definition and dependency logic live in one place
- the Python runtime can validate and rehydrate task files consistently
- the JS side no longer needs to parse or own task file loading behavior
- the boundary between orchestration and execution becomes explicit

### Negative

- the task pool now crosses the process boundary as serialized JSON
- changes to task schema must stay compatible with the JS snapshot consumer
- current task state is still duplicated in runtime memory on both sides

### Neutral

- JS still needs a thin in-memory structure to drive live execution
- the existing Mineflayer execution model remains unchanged

## Related Files

- `mindcraft_py/cli.py`
- `mindcraft_py/runtime.py`
- `mindcraft_py/task_coordinator.py`
- `main.js`
- `src/agent/tasks/task_pool.js`
- `src/agent/agent.js`
- `tests/test_runtime_task_file_loader.py`
- `tests/test_cli.py`
