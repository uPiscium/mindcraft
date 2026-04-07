# Repository Guide

This repo is a Minecraft agent framework with both JS and Python runtime pieces.
Use this file as the default operating guide for agentic edits in this workspace.

## Project Shape

- Runtime entry points: `main.js`, `mindcraft_py/__main__.py`
- Primary app code: `src/mindcraft/`, `src/models/`, `src/process/`, `src/utils/`, `mindcraft_py/`
- Example agents and profiles: `agents/`, `profiles/`
- Task definitions: `tasks/`
- Current test file(s): `tests/`
- ESLint config: `eslint.config.js`
- Migration focus: keep JS as the Mineflayer/UI bridge and move Mineflayer-independent runtime/state logic into `mindcraft_py/`

## Commands

### Install

```bash
just test
```

### Start the app

```bash
python -m mindcraft_py --profiles ./agents/Andy.toml
```

Equivalent direct entry:

```bash
node main.js
```

Python entrypoint notes:

- `mindcraft_py` owns the runtime/state/process layer.
- JS `mindserver` stays as the visible UI/Socket.IO layer for now.

### Run a task file

```bash
node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```

### Lint

Use the repository task runner for the standard checks:

```bash
just lint
```

Format code:

```bash
just fmt
```

Run the full verification suite:

```bash
just check
```

### Tests

Run the test suite:

```bash
just test
```

Run a single test file directly when you need targeted feedback:

```bash
uv run --group dev pytest tests/<test-file>.py
```

If you add more tests, keep them runnable through the existing task runner or direct test command.

### Build

There is no separate build step.
The closest validation is:

```bash
just check
```

## Style Rules

### Modules and imports

- Use the idioms of the file's language and runtime.
- Prefer explicit imports/exports over implicit globals.
- Group imports by origin: standard library/built-ins, third-party packages, then local files.
- Keep import paths explicit and file extensions included for local files when the language requires them.
- Prefer named imports when only one or two bindings are needed.
- Keep imports alphabetized within each group when practical.

### Formatting

- Use the project's formatter/linter conventions.
- Keep indentation consistent with the surrounding file.
- Prefer trailing commas only when the surrounding file already uses them.
- Keep line length reasonable; wrap long argument lists and object literals.
- Avoid noisy formatting churn; follow the surrounding file's local style.

### Syntax and types

- Favor clear runtime checks over unnecessary abstraction.
- Use immutable bindings by default; use mutable bindings only when reassignment is required.
- Keep functions small and single-purpose where possible.
- Prefer explicit object/data shapes over deep nested mutation.

### Naming

- Classes and constructors use `PascalCase`.
- Functions and variables use `camelCase`.
- Use `SCREAMING_SNAKE_CASE` only for true constants.
- Name files to match their main export or responsibility.
- Use descriptive names for agent/model/runtime concepts; avoid abbreviations unless already established.

### Async and promises

- Await promises or handle them explicitly.
- Do not introduce fire-and-forget async work unless there is a clear reason and the error path is handled.
- Prefer `async`/`await` over chained `.then()` calls for new code.
- Use `try`/`catch` around external I/O, process spawning, and network calls.

### Error handling

- Fail fast on invalid user input or missing required config.
- Keep error messages actionable and specific.
- Preserve the original error when rethrowing if it carries useful context.
- Log only once per failure path when possible.
- Handle network timeouts and external service failures gracefully.
- When a recoverable error occurs, return a structured `{ success, error }` style result if the surrounding API already uses that pattern.

### Control flow

- Curly braces are not strictly required by lint, but use them when they improve readability or prevent ambiguity.
- Prefer early returns for invalid states.
- Avoid deeply nested branching; split helpers instead.
- Be careful with mutation of shared objects; clone when a function should not mutate caller state.

### Logging

- Use the existing logging style of the surrounding module.
- Keep logs concise and operational.
- Do not add verbose debug logging unless it materially helps debugging.

## Repository-Specific Patterns

- `settings.js` is the central runtime configuration object for the JS side; it is mutated by `main.js` based on CLI args and environment variables.
- `mindcraft_py/` contains the Python runtime/state layer and should be kept aligned with the JS-facing wrappers.
- `README.py.md` and `impl-plan.md` describe the current migration state and should be kept in sync with code changes.
- `src/utils/text.js` contains message-shaping helpers used by model adapters; be careful not to change turn ordering semantics casually.
- `src/models/ollama.js` shows the expected adapter pattern: request shaping, retry handling, and normalization of model output.
- `src/process/agent_process.js` handles process lifecycle and restart behavior; keep signal handling and restart safeguards intact.
- `src/mindcraft/agent_registry.js` is the thin bridge for shared agent state on the JS side.
- Final verification should include `just test`, `just check`, and a live startup check when feasible.

## Testing Guidance

- Prefer adding a focused test in `tests/` for behavioral changes.
- If a change affects a model adapter, add a narrow regression test near the affected logic.
- Run the most specific test file first, then the full verification task before finishing.
- For cross-file changes, validate the affected startup path with the relevant entry point if feasible.

## When Editing

- Match the existing module’s tone and level of abstraction.
- Keep changes minimal and targeted.
- Do not rewrite unrelated code while touching a file.
- Preserve file-local conventions already established in that module.
- If you touch a runtime path, verify there is no accidental promise leak or unhandled rejection.

## Rules Sources

- No `.cursor/rules/` directory was present in this repository snapshot.
- No `.cursorrules` file was present.
- No `.github/copilot-instructions.md` file was present.

## Practical Defaults

- For most edits: run the most targeted `just` task and the relevant direct test command.
- For startup issues: inspect `main.js`, `settings.js`, and the relevant module in `src/`.
- For model behavior changes: verify the adapter against `src/models/ollama.js` style and update or add a regression test.
