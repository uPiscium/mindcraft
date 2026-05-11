# 0001 Bootstrap Entry Contract

## Status
Accepted

## Context
The existing entrypoint mixes CLI parsing, environment merging, task loading, and runtime startup. The bootstrap phase needs to become testable without changing the current startup behavior.

## Decision
- Keep environment-specific overrides stronger than CLI arguments for `MINECRAFT_PORT`, `MINDSERVER_PORT`, `PROFILES`, `INSECURE_CODING`, `BLOCKED_ACTIONS`, `MAX_MESSAGES`, `NUM_EXAMPLES`, and `LOG_ALL`.
- Keep `SETTINGS_JSON` handling in `settings.js` as the base configuration layer.
- Move CLI/env merging, task loading, and validation into a dedicated bootstrap module.
- Require `task_id` when `task_path` is provided.
- Use a single bootstrap context object for downstream startup.

## Consequences
- `main.js` becomes a thin entrypoint.
- Bootstrap logic can be unit-tested without launching MineCraft or the UI.
- Error messages should point to the missing bootstrap input instead of failing deep in runtime startup.
