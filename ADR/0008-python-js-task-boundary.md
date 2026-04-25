# ADR 0008: Python/JS Task Responsibility Boundary

## Status

Accepted

## Context

The runtime now has a Python-owned task coordinator, slot orchestration, and assigned-task controller. JS still owns the Mineflayer execution loop, self-prompting, and action handling.

The remaining question is not whether Python should replace JS execution entirely, but how to draw a stable boundary so task management stays consistent while Mineflayer-specific behavior remains in JS.

## Decision

We will define Python as the source of truth for task management and state transitions, and JS as the execution boundary for Mineflayer actions and self-prompt-driven runtime behavior.

The chosen split is:

- Python owns task loading, normalization, dependency resolution, selection, assignment, completion, yielding, and slot state
- JS owns Mineflayer connection, movement, interaction, self-prompting, and action execution
- Python may tell JS which task is current, but JS remains responsible for carrying out that task in the live agent loop
- JS may auto-start or auto-advance tasks, but the canonical task lifecycle state remains in Python

## Consequences

### Positive

- task definition and lifecycle logic remain centralized in Python
- Mineflayer-specific behavior stays in the layer that can actually perform it
- the boundary is explicit, so future migration work has a stable contract
- assigned-task execution and self-directed execution can share the same Python task state

### Negative

- task state is still mirrored across the process boundary at runtime
- JS must continue to keep a thin in-memory task representation
- auto-start and auto-advance behavior still depends on the JS loop

### Neutral

- this does not require removing the JS task pool immediately
- BFS execution remains a Python-side option for dependency-following runs

## Related Files

- `mindcraft_py/runtime.py`
- `mindcraft_py/task_coordinator.py`
- `mindcraft_py/task_slot.py`
- `mindcraft_py/task_slot_orchestrator.py`
- `mindcraft_py/task_execution_controller.py`
- `src/agent/agent.js`
- `src/agent/self_prompter.js`
- `src/agent/tasks/task_pool.js`
