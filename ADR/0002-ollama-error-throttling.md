# 0002 Ollama Error Throttling

## Status
Accepted

## Context
Repeated embedding requests can fail in environments where Ollama is unreachable. The current implementation logs the same network failure many times, which obscures the real startup signal.

## Decision
- Log the Ollama request failure only once per unique failure signature in a process.
- Keep the actual failure behavior unchanged so callers can still fall back to word-overlap matching.
- Do not change embedding retry semantics in this step.

## Consequences
- Startup logs become readable again when multiple agents initialize.
- The first failure remains visible for diagnosis.
- Identical later failures are suppressed.
