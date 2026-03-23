# Testing

- Run the narrowest useful test first.
- Prefer a single pytest target when iterating on Python changes.
- Validate bridge changes with at least one mock integration test.
- Validate multi-agent changes with a representative live task when possible.
- Use `ruff check` and `ruff format --check` for Python edits.
- Use `eslint` for JS edits.

Recommended order:
1. Unit test for the changed module.
2. Bridge or mock integration test.
3. Full Python suite.
4. Representative live task if the change affects runtime behavior.
