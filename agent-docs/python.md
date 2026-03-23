# Python Runtime

- Python entrypoint: `main.py`
- Runtime wrapper: `mindcraft_py/runtime.py`
- Config loading: `mindcraft_py/config.py`
- Profile loading: `mindcraft_py/profiles.py`
- Command registry: `mindcraft_py/commands.py`
- Command catalog generation: `mindcraft_py/catalog.py`

## Settings

- `settings.toml` is preferred when present.
- `settings.js` remains the fallback source.
- `agents/*.json` and `agents/*.toml` are both supported by the Python runtime.

## Profiles

- Prefer TOML profiles for new work when possible.
- Keep the `name` field consistent with the agent identity used in tasks and logs.

## Bridge notes

- Python talks to MindServer over Socket.IO.
- Query/action bridge commands are handled through the runtime helper methods.
