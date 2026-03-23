# Command Catalog

- The Python registry is the source of truth for the generated command catalog.
- Generate the catalog with `just catalog`.
- The generated file is `mindcraft_py/command_catalog.json`.
- JS prompt docs load that generated catalog when available.
- Keep command names, descriptions, and parameter docs synchronized across JS and Python.
