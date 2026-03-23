# Commands

## Setup

```bash
npm install
uv sync
uv sync --group dev
```

## Run

```bash
npm start
node main.js
uv run python main.py
uv run python -m mindcraft_py
```

## Single task

```bash
uv run python main.py --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```

## Lint / format

```bash
npx eslint .
uv run --group dev ruff check .
uv run --group dev ruff format .
```

## Tests

```bash
uv run --group dev pytest
uv run --group dev pytest tests/test_python_commands.py::test_default_registry_matches_javascript_specs
uv run --group dev pytest tests/test_action_bridge_mock.py
```

## Just

```bash
just test
just lint
just fmt
just check
just catalog
```

Use `just catalog` to regenerate `mindcraft_py/command_catalog.json`.
