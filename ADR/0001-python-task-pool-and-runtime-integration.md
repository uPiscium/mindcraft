# ADR 0001: Python Task Pool and Runtime Integration

## Status

Accepted

## Context

The repository is migrating runtime and state responsibilities from JavaScript into `mindcraft_py` while keeping Mineflayer-specific behavior in the JS bridge. During this work, a centralized task pool was implemented and then connected to the Python runtime lifecycle.

The implemented pieces are:

- `mindcraft_py.task_coordinator.CentralTaskCoordinator`
- `mindcraft_py.runtime.MindcraftRuntime` task-pool delegation
- `depends_on`-based task acquisition filtering
- runtime-level task registration and cleanup on lifecycle events
- focused unit and integration tests for coordinator and runtime behavior

## Decision

We will keep task orchestration inside Python and expose it through `MindcraftRuntime` as the integration boundary.

The chosen model is:

- tasks are registered through runtime APIs or settings-derived inputs
- `CentralTaskCoordinator` owns atomic acquire/yield behavior
- tasks may declare `depends_on` prerequisites by task id
- a task is eligible only when it is `AVAILABLE` and all dependencies are `COMPLETED`
- agent lifecycle hooks seed, acquire, yield, and clear tasks without moving Mineflayer-specific logic out of JS beyond the runtime boundary

## Consequences

### Positive

- task coordination remains deterministic and testable in Python
- runtime integration stays thin and delegates policy to the coordinator
- task dependencies can be expressed without introducing a separate queue system
- shutdown and stop paths can clean up locked tasks consistently

### Negative

- the runtime now carries more state for agent/task coupling
- task lifecycle behavior must stay aligned across coordinator, runtime, and tests
- the dependency model currently relies on in-memory task state and does not persist across restarts

### Neutral

- capability-based filtering was removed in favor of a simpler dependency-driven model
- task visibility remains exposed through runtime APIs for debugging and orchestration

## Related Files

- `mindcraft_py/task_coordinator.py`
- `mindcraft_py/runtime.py`
- `tests/test_task_coordinator.py`
- `tests/test_task_coordinator_unit.py`
- `tests/test_runtime_task_pool.py`
- `tests/test_runtime_task_pool_unit.py`
- `tests/test_runtime_task_pool_integration.py`
- `README.py.md`
- `impl-plan/v1.md`
- `impl-plan/v1.1.md`
- `impl-plan/v2.1.md`
