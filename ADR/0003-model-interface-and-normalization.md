# 0003 Model Interface and Normalization

## Status
Accepted

## Context
The codebase already has multiple provider-specific methods and several model descriptor shapes. The refactor needs a single execution path without breaking existing call sites.

## Decision
- Normalize model descriptors into a common `{ api, model, url, params }` shape before provider creation.
- Expose a common `chat()` method on provider implementations while keeping `sendRequest()` intact for compatibility.
- Treat unsupported provider APIs as early errors during model resolution.

## Consequences
- Callers can move to `chat()` without an all-at-once migration.
- String and object model forms resolve through the same path.
- Provider addition depends on registry updates instead of ad hoc conditionals.
