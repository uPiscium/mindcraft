# Workflow

1. Read the target files and nearby code before editing.
2. Identify whether the change belongs in JS, Python, or a bridge layer.
3. Make the smallest change that solves the problem.
4. Prefer one focused test over the whole suite while iterating.
5. Run the relevant formatter/linter after edits.
6. Validate one representative integration path when changing bridge or runtime code.
7. Summarize what changed, what was validated, and any remaining caveats.

Avoid overwriting unrelated user work in a dirty tree.
