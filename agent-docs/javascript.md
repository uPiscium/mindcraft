# JavaScript Runtime

- JS entrypoint: `main.js`
- MindServer: `src/mindcraft/mindserver.js`
- Agent process: `src/process/agent_process.js`
- Mock agent: `src/process/mock_agent_client.js`

## Runtime boundaries

- JS owns Mineflayer, command execution, and the actual bot process.
- Python can request bridge work, but Mineflayer implementation stays in JS.
- Keep bridge event names explicit and narrow.

## Patch-package

- If `patch-package` warns about version mismatches, regenerate the relevant patch files and verify behavior before committing.
