# AGENTS.md

Practical guidance for coding agents working in this repository.

## Overview

- `mindcraft` is primarily a Node.js ESM project with a Python runtime layer.
- JavaScript owns Mineflayer, agent behavior, command execution, and MindServer.
- Python owns the newer runtime wrapper, settings resolution, command-registry work, and tests under `tests/`.
- Main JS entrypoint: `main.js`.
- Main Python entrypoint: `main.py`.
- Core JS code lives in `src/`.
- Python runtime code lives in `mindcraft_py/`.
- Automation and analysis scripts live in `tasks/`.

## Environment Setup

- Node version: prefer `18` or `20` LTS per project docs.
- Python version: `3.11+`.
- Install Node dependencies with `npm install`.
- Install Python dependencies with `uv sync` and `uv sync --group dev`.
- If using Nix, `flake.nix` includes the core dev tools, including `just`; enter with `nix develop`.

## Build And Run Commands

- Standard JS runtime:
```bash
npm start
node main.js
```
- Python runtime:
```bash
uv run python main.py
uv run python -m mindcraft_py
```
- Explicit profiles:
```bash
node main.js --profiles ./agents/Andy.json ./agents/Bob.json
uv run python main.py --profiles ./agents/Andy.json ./agents/Bob.json
```
- Single task:
```bash
node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
uv run python main.py --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```
- Docker:
```bash
docker build -t mindcraft .
docker compose up --build
```

## Lint Commands

- JavaScript linting uses ESLint directly; there is no npm lint script.
- `npx eslint .`
- `npx eslint src main.js settings.js`
- `npx eslint src/agent/agent.js`

- Python linting uses Ruff.
- `uv run --group dev ruff check .`
- `uv run --group dev ruff check mindcraft_py tests`
- `uv run --group dev ruff check tests/test_python_commands.py`

## Format Commands

- Python formatting also uses Ruff.
- `uv run --group dev ruff format .`
- `uv run --group dev ruff format mindcraft_py tests`
- `uv run --group dev ruff format tests/test_mock_query_bridge.py`
- Formatting check only: `uv run --group dev ruff format --check .`

## Test Commands

- Full Python suite: `uv run --group dev pytest`
- Single Python test file:
```bash
uv run --group dev pytest tests/test_python_commands.py
uv run --group dev pytest tests/test_mock_query_bridge.py
```
- Single test function:
```bash
uv run --group dev pytest tests/test_python_commands.py::test_default_registry_matches_javascript_specs
uv run --group dev pytest tests/test_mock_query_bridge.py::test_mock_query_bridge_runs_without_minecraft
```
- Verbose single-test debug: `uv run --group dev pytest -vv tests/test_python_commands.py::test_execute_query_uses_runtime_bridge`
- Representative JS integration validation: `node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs`
- Python task helpers:
```bash
python tasks/run_task_file.py --task_path tasks/basic/single_agent.json
python tasks/evaluation_script.py --check experiments/<exp_folder>
```

## Just Commands

- Prefer `just` for common Python checks: `just test`, `just lint`, `just fmt`, `just check`.
- In Nix environments use `nix develop --command just check`.

## Current Test Coverage Notes

- `tests/test_python_commands.py` covers Python command parsing, docs generation, spec matching, and query-bridge unit behavior.
- `tests/test_mock_query_bridge.py` covers Python-to-JS query bridge behavior without Minecraft running.
- The mock path uses `mock_client` and does not validate true Mineflayer world behavior.
- For real Mineflayer behavior, run a JS or Python task against a live Minecraft server/world.

## JavaScript Style

- Use ESM `import` / `export` only.
- Follow the existing semicolon style; ESLint requires semicolons.
- Match the touched file's quote style, but many files use single quotes.
- Prefer `const`; use `let` only when reassignment is necessary.
- Keep imports at the top of the file and preserve local ordering unless there is a reason to change it.
- Many JS files use 4-space indentation; match the file you are editing.
- Use `camelCase` for variables and functions.
- Use `PascalCase` for classes.
- Preserve existing filename conventions such as `snake_case.js` where already used.

## Python Style

- Follow Ruff defaults configured in `pyproject.toml`.
- Target Python `3.11+` features only.
- Keep lines within Ruff's configured width of `88`.
- Sort imports in Ruff-compatible order.
- Use `snake_case` for functions, variables, and module names.
- Use `PascalCase` for classes.
- Use dataclasses where the code already models structured records that way.
- Keep CLI scripts explicit and simple; `argparse` is the established pattern.
- Prefer `Path` or explicit path joins over fragile relative string handling.

## Types And Data Modeling

- There is no TypeScript in the repo today; do not introduce TS unless explicitly requested.
- In JS, use guard clauses and explicit runtime checks for external inputs.
- In Python, use type hints when they improve clarity and match nearby code.
- When mirroring JS concepts in Python, keep naming aligned so spec comparisons remain easy.
- For command specs, preserve exact command names, descriptions, and parameter docs when intended to match JS.

## Async, Errors, And Process Handling

- ESLint enforces `require-await` and disallows floating promises.
- Always `await` async work or handle the promise explicitly.
- Wrap risky network, file, subprocess, and model calls in `try` / `catch` or `try` / `except`.
- Error messages should include enough context to act on them.
- Do not silently swallow errors.
- Preserve existing process-lifecycle behavior around MindServer, agent restarts, and shutdown flows.
- Be careful with long-running subprocesses and socket connections; ensure cleanup paths remain intact.

## Naming And Architecture Conventions

- Keep JavaScript as the owner of Mineflayer-specific behavior unless intentionally migrating a boundary.
- Keep Python orchestration thin unless the task is specifically about moving responsibility into Python.
- New bridge APIs should be narrowly scoped and explicit about direction: Python -> MindServer -> JS agent.
- For mock-only behavior, name it clearly as mock/test-only and avoid blending it into production paths accidentally.

## Security And Safety

- Treat `allow_insecure_coding` and `!newAction` as high-risk features.
- Never commit secrets such as `keys.json`, `.env`, tokens, or credentials.
- Avoid destructive git or filesystem operations unless explicitly requested.
- Respect a dirty working tree; do not overwrite unrelated user edits.
- Do not weaken sandboxing or security-related checks without a clear request.

## Cursor And Copilot Rules

- Checked paths: `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`
- Result: none are present right now.
- If any of these files are added later, treat them as repository-local instructions with high priority.

## Recommended Agent Workflow

1. Read the target files plus their immediate neighbors before editing.
2. Check whether the change belongs in JS, Python, or a bridge layer.
3. Make minimal edits that match existing local style.
4. Run the narrowest useful test first, especially a single pytest target when available.
5. Run Ruff on touched Python files and ESLint on touched JS files.
6. For bridge changes, prefer validating both unit tests and one representative integration path.
7. Report any assumptions, limitations, and what was actually verified.
