# ADR 0002: TOML Task Pool File Loader

## Status

Accepted

## Context

The task pool already supports in-memory task registration, dependency tracking via `depends_on`, and lifecycle integration through `MindcraftRuntime`. What was still missing was a file-based way to define multiple tasks for the task pool without relying on the older `main.js` task file shape.

We wanted a format that can express:

- multiple tasks in one file
- dependency edges between tasks
- explicit priorities
- simple startup loading into the Python runtime

## Decision

We will use TOML with a `[[tasks]]` array for task pool files.

The runtime exposes `load_task_pool_file(task_file_path)` and accepts `task_pool_file` from settings, profiles, or the CLI. Loaded tasks are registered into the shared `CentralTaskCoordinator` and validated for missing dependencies.

## Consequences

### Positive

- task files are human-readable and easy to version
- multiple tasks and dependency chains can live in one file
- the file format is independent from the legacy single-task JSON flow
- runtime startup can preload a task pool without extra wiring in the caller

### Negative

- TOML parsing is now part of runtime startup for task-pool files
- dependency validation happens at load time, so invalid files fail fast
- file-based loading increases the surface area of runtime configuration

### Neutral

- `main.js` keeps its historical task-path flow separate from the new task pool loader
- the loader is intentionally file-format specific and does not attempt to normalize old task definitions

## Related Files

- `mindcraft_py/runtime.py`
- `mindcraft_py/cli.py`
- `main.js`
- `tasks/task_pool_demo.toml`
- `tests/test_runtime_task_file_loader.py`
- `impl-plan/task-pool-file-loader.md`
