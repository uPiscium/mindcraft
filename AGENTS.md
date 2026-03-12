# AGENTS.md

Practical instructions for agentic coding tools operating in this repository.

## Repository Overview

- Runtime: Node.js ESM project (`"type": "module"`).
- Main entrypoint: `main.js`.
- Core implementation: `src/`.
- Task/evaluation automation: `tasks/` (mostly Python).
- Lint config: `eslint.config.js`.
- No dedicated unit-test framework config found (no Jest/Vitest/Pytest config files).

## Setup

### Node environment

- Prefer Node `v18` or `v20` LTS (per README guidance).

```bash
npm install
npm start
```

`npm start` runs `node main.js`.

### Python environment (evaluation scripts)

`pyproject.toml` is minimal; practical dependencies are in `requirements.txt`.

```bash
conda create --name mindcraft python=3.11
conda activate mindcraft
pip install -r requirements.txt
```

## Build, Lint, and Test Commands

## Build / run commands

No transpile step is required for app code.

```bash
npm install
npm start
docker build -t mindcraft .
docker compose up --build
```

## Lint commands

No npm lint script is defined; run ESLint directly:

```bash
# full repository
npx eslint .

# common source scope
npx eslint main.js settings.js src tasks

# single-file lint
npx eslint src/agent/agent.js
```

## Test commands (single-test guidance)

There is no formal test runner configured. Use integration-style validation.

### Best single-test equivalent

```bash
node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```

### Run all tasks in one task file

```bash
python tasks/run_task_file.py --task_path tasks/single_agent/crafting_train.json
```

`run_task_file.py` iterates over all task IDs in the file.

### Evaluate an existing results folder

```bash
python tasks/evaluation_script.py --check experiments/<exp_folder>
```

### Example benchmark run

```bash
python tasks/evaluation_script.py \
  --task_path tasks/crafting_tasks/test_tasks/2_agent.json \
  --model gpt-4o-mini \
  --template_profile profiles/tasks/crafting_profile.json
```

## Common Runtime Commands

```bash
# run with explicit profiles
node main.js --profiles ./profiles/andy.json ./profiles/jill.json

# run one specific task
node main.js --task_path <task_file.json> --task_id <task_id>
```

Environment variable overrides read by `main.js`:

- `MINECRAFT_PORT`
- `MINDSERVER_PORT`
- `PROFILES` (JSON array string)
- `INSECURE_CODING`
- `BLOCKED_ACTIONS` (JSON)
- `MAX_MESSAGES`
- `NUM_EXAMPLES`
- `LOG_ALL`

## Code Style Guidelines

Derived from ESLint and existing repository conventions.

## JavaScript / ESM

- Use ESM imports/exports.
- Use semicolons (required by ESLint).
- Prefer single quotes unless interpolation or local file style differs.
- Prefer `const`; use `let` only for reassignment.
- Avoid introducing CommonJS in new code.

## Imports

- Keep imports at the top of files.
- Match local ordering in touched files.
- Do not reorder unrelated imports without reason.

## Formatting

- Match file indentation (many files use 4 spaces).
- Avoid trailing whitespace.
- Keep complex logic readable; avoid dense one-liners.
- `curly` is not enforced, but explicit braces are preferred.

## Types, Naming, and Structure

- No TypeScript currently; use runtime validation and guard clauses.
- Classes: `PascalCase`.
- Functions/methods/variables: `camelCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Preserve local filename conventions (many files use `snake_case.js`).

## Error Handling and Async

- Wrap risky IO/network/model calls with `try/catch`.
- Fail fast on invalid critical config.
- Provide actionable error messages with context.
- Never silently swallow errors.
- ESLint enforces no floating promises and disallows async without `await`.
- Always `await` async operations or handle promises explicitly.

## Python Script Conventions

- Follow existing `argparse` CLI patterns in `tasks/*.py`.
- Keep path handling explicit and robust.
- Surface parse/file errors clearly.

## Safety Guidance

- Treat `allow_insecure_coding` flows as high-risk execution paths.
- Never commit secrets (`keys.json`, `.env`, credentials).
- Avoid destructive filesystem/git operations unless explicitly requested.
- Preserve unrelated user changes in a dirty working tree.

## Cursor and Copilot Rules

Checked for local instruction files:

- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

Result: none are present in this repository at this time.
If these files are added later, treat them as higher-priority local instructions.

## Recommended Agent Workflow

1. Read target files and nearby dependencies first.
2. Make minimal, scoped edits matching local style.
3. Lint touched files (`npx eslint <paths>`).
4. Run one representative task command for behavior validation.
5. Report assumptions and verification steps in your final message.
