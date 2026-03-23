set shell := ["bash", "-cu"]

default:
    @just --list

test:
    uv run --group dev pytest

lint:
    uv run --group dev ruff check .

fmt:
    uv run --group dev ruff format .

check:
    uv run --group dev pytest
    uv run --group dev ruff check .
    uv run --group dev ruff format --check .

catalog:
    uv run python -c "from mindcraft_py.catalog import write_command_catalog; write_command_catalog()"
