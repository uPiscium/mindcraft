# Repository Guide

This repo is a Node.js/Minecraft agent framework with many runtime modules and a small amount of test coverage.
Use this file as the default operating guide for agentic edits in this workspace.

## Project Shape

- Runtime entry point: `main.js`
- Primary app code: `src/mindcraft/`, `src/models/`, `src/process/`, `src/utils/`
- Example agents and profiles: `agents/`, `profiles/`
- Task definitions: `tasks/`
- Current test file(s): `tests/`
- ESLint config: `eslint.config.js`

## Commands

### Install

```bash
npm install
```

### Start the app

```bash
npm start
```

Equivalent direct entry:

```bash
node main.js
```

### Run a task file

```bash
node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```

### Lint

There is no dedicated `npm run lint` script. Use ESLint directly:

```bash
npx eslint .
```

Lint a single file:

```bash
npx eslint src/models/ollama.js
```

Lint a directory:

```bash
npx eslint src/models
```

### Tests

There is no test runner script in `package.json`. Run test files directly with Node:

```bash
node tests/test_ollama_client.js
```

Run a single test file by path the same way:

```bash
node tests/<test-file>.js
```

If you add more tests, keep them executable with plain `node` unless the repo grows a dedicated runner.

### Build

There is no formal build step.
The closest validation is:

```bash
npx eslint . && node tests/test_ollama_client.js
```

## Style Rules

### Modules and imports

- Use ES modules everywhere; this repo is configured with `"type": "module"`.
- Prefer `import`/`export` over CommonJS.
- Group imports by origin: built-ins, third-party packages, then local files.
- Keep import paths explicit and file extensions included for local imports.
- Prefer named imports when only one or two bindings are needed.
- Keep imports alphabetized within each group when practical.

### Formatting

- Use semicolons; ESLint enforces them.
- Prefer single quotes for strings in JS source when editing existing code.
- Use 4-space indentation in this codebase.
- Prefer trailing commas only when the surrounding file already uses them.
- Keep line length reasonable; wrap long argument lists and object literals.
- Avoid noisy formatting churn; follow the surrounding file’s local style.

### Syntax and types

- This is plain JavaScript, not TypeScript.
- Favor clear runtime checks over type annotations.
- Use `const` by default; use `let` only when reassignment is required.
- Avoid `var`.
- Keep functions small and single-purpose where possible.
- Prefer explicit object shapes in code over deep nested mutation.

### Naming

- Classes and constructors use `PascalCase`.
- Functions and variables use `camelCase`.
- Use `SCREAMING_SNAKE_CASE` only for true constants.
- Name files to match their main export or responsibility.
- Use descriptive names for agent/model/runtime concepts; avoid abbreviations unless already established.

### Async and promises

- Await promises or handle them explicitly; `no-floating-promise` is enabled.
- Do not introduce fire-and-forget promises unless there is a clear reason and the error path is handled.
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

- Use `console.log`/`console.warn`/`console.error` consistently with the surrounding module.
- Keep logs concise and operational.
- Do not add verbose debug logging unless it materially helps debugging.

## Repository-Specific Patterns

- `settings.js` is the central runtime configuration object; it is mutated by `main.js` based on CLI args and environment variables.
- `src/utils/text.js` contains message-shaping helpers used by model adapters; be careful not to change turn ordering semantics casually.
- `src/models/ollama.js` shows the expected adapter pattern: request shaping, retry handling, and normalization of model output.
- `src/process/agent_process.js` handles process lifecycle and restart behavior; keep signal handling and restart safeguards intact.
- Many files assume browser globals or Node globals configured through ESLint; do not add globals casually.

## Testing Guidance

- Prefer adding a focused Node-executable test in `tests/` for behavioral changes.
- If a change affects a model adapter, add a narrow regression test near the affected logic.
- Run the most specific test file first, then `npx eslint .` before finishing.
- For cross-file changes, validate the affected startup path with `node main.js` if feasible.

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

- For most edits: run `npx eslint <file>` and the relevant `node tests/<file>.js` test.
- For startup issues: inspect `main.js`, `settings.js`, and the relevant module in `src/`.
- For model behavior changes: verify the adapter against `src/models/ollama.js` style and update or add a regression test.
