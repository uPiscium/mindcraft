# TypeScript Migration Log

- Tightened the TypeScript/lint setup so TS files are checked by `tsc` and ESLint.
- Migrated core agent files to TypeScript: `agent.ts`, `coder.ts`, `history.ts`, `vision_interpreter.ts`, `camera.ts`, `agent_process.ts`, and `init_agent.ts`.
- Added/updated shared type declarations under `src/types/` and Mineflayer bot augmentation in `src/types/modules.d.ts`.
- Cleaned up `world.ts` and `skills.ts` type boundaries so shared world helpers and skill helpers compile cleanly.
- Removed the temporary `// @ts-nocheck` from `skills.ts` after finishing the type pass.

Verification:
- `npx tsc --noEmit`
- `npx eslint src/agent/library/skills.ts`
- `npx eslint src/agent/agent.ts src/agent/coder.ts src/agent/history.ts src/agent/library/world.ts src/agent/vision/vision_interpreter.ts src/types/modules.d.ts`
