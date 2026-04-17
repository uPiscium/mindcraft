# ADR 0003: Task Pool Execution Loop Integration

## Status

Accepted

## Context

The runtime now supports loading dependency-aware task pool files, registering tasks into `MindcraftRuntime`, and exposing the current task through agent state. The remaining gap was connecting that task state to the real execution loop so that tasks are automatically consumed, completed, or yielded as the agent runs.

We needed a minimal integration that:

- keeps the existing Minecraft action system intact
- makes the current task visible to the agent prompt and state
- automatically advances task state on success or failure
- recovers tasks on disconnect, stop, or shutdown

## Decision

We will keep the task pool inside the agent/runtime layer and integrate it with the existing action lifecycle.

The integration model is:

- load a TOML task pool file at startup through `task_pool_file`
- create an in-memory `TaskPool` per agent
- acquire the next available task during agent startup and whenever the agent becomes idle
- expose the current task to the agent via `self_prompter` and `full_state`
- mark the current task `COMPLETED` when an action succeeds
- mark the current task `AVAILABLE` again when an action fails or the agent is interrupted
- clear the task context on completion, failure, disconnect, or shutdown

## Consequences

### Positive

- tasks now influence the live agent loop instead of existing only as stored state
- dependency chains can advance automatically without manual intervention
- the current task is visible in logs and full state output
- failure and interruption paths recover locked tasks instead of leaving them stuck

### Negative

- task lifecycle is now coupled to the action manager and self-prompter
- task completion is currently coarse-grained and still follows action success/failure rather than a separate planner
- the integration remains in-memory and does not persist task progress across restarts

### Neutral

- the existing self-prompting and command execution system remains the source of actual movement and interaction
- the task pool acts as a coordinator over that existing loop rather than replacing it

## Related Files

- `src/agent/tasks/task_pool.js`
- `src/agent/self_prompter.js`
- `src/agent/action_manager.js`
- `src/agent/agent.js`
- `src/agent/library/full_state.js`
- `main.js`
- `tasks/task_pool_demo.toml`
- `tests/test_runtime_task_file_loader.py`
- `tests/test_runtime_task_pool_integration.py`

## Implementation Notes

- The execution loop is intentionally coarse-grained and currently advances on action success/failure rather than a separate planner.
- The task pool is still in-memory and the integration relies on the existing Minecraft action lifecycle.
