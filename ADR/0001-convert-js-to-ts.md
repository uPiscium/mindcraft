Title: Convert all .js files to .ts

Status: Proposed

Context:
- The repository currently uses ES modules (.js) and has "type": "module" in package.json.
- There are many .js files across src/, tasks/, and root entrypoints. We will convert all .js files to .ts to move toward TypeScript.

Decision:
- Rename all .js files to .ts and update internal import paths to reference .ts files (where explicit).
- Do not add a full TypeScript compiler configuration or enable strict type checking in this change to keep scope minimal.
- Add minimal type annotations where straightforward (function parameters/returns) only when low-risk; otherwise keep code unchanged except for extensions and small adjustments to satisfy TS parsing (e.g. export default vs module.exports). The goal is a mechanical conversion rather than a deep type migration.

Consequences:
- Pros: uniform file extensions, easier future type migrations, better editor support.
- Cons: Type errors may appear when running tsc; we avoid enabling tsc in CI for this change. Some third-party modules may need type declarations down the road.

Follow-ups:
1. Add a tsconfig.json and progressively enable checks.
2. Introduce .d.ts shims for untyped dependencies if needed.
3. Incrementally add types and convert any remaining CommonJS patterns.
