# Style

## JavaScript

- Use ESM `import` / `export` only.
- Keep semicolons.
- Prefer `const`; use `let` only when reassignment is needed.
- Keep imports at the top and follow local file conventions.
- Use `camelCase` for variables/functions and `PascalCase` for classes.
- Preserve existing filenames and module boundaries.

## Python

- Follow Ruff defaults and the configured 88 character line length.
- Use `snake_case` for functions, variables, and modules.
- Use `PascalCase` for classes.
- Prefer explicit types when they help readability.
- Keep CLI code simple and `argparse`-based.
- Use dataclasses for structured records when it matches nearby code.

## Data and interfaces

- Keep JS ownership for Mineflayer-specific behavior unless intentionally migrating a boundary.
- Keep Python orchestration thin unless the task is about moving responsibility into Python.
- Keep command names and parameter docs aligned across registries and docs.
