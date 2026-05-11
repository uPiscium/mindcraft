import { Agent } from '../agent/agent'; // 推測: 適切な型定義（.d.ts）が存在すること
import { serverProxy } from '../agent/mindserver_proxy';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

// パース後の引数の型を定義
interface AgentArgs {
  name: string;
  load_memory: boolean;
  init_message: string | null;
  count_id: number;
  port: number;
}

// 1. hideBinを使用してprocess.argvを正しく処理
// 2. 必須項目（demandOption）を定義し、手動のlengthチェックを排除
// 3. parseSync()で同期的に型付きの引数を取得
const argv: AgentArgs = yargs(hideBin(process.argv))
  .option('name', {
    alias: 'n',
    type: 'string',
    description: 'name of agent',
    demandOption: true, // 必須化（推測: 接続に必須であるため）
  })
  .option('load_memory', {
    alias: 'l',
    type: 'boolean',
    default: false,
    description: 'load agent memory from file on startup',
  })
  .option('init_message', {
    alias: 'm',
    type: 'string',
    default: null,
    description: 'automatically prompt the agent on startup',
  })
  .option('count_id', {
    alias: 'c',
    type: 'number',
    default: 0,
    description: 'identifying count for multi-agent scenarios',
  })
  .option('port', {
    alias: 'p',
    type: 'number',
    description: 'port of mindserver',
    demandOption: true, // 必須化（推測: 接続に必須であるため）
  })
  .help() // --help オプションを自動生成
  .parseSync();

void (async () => {
  try {
    console.log(`Connecting to MindServer (Name: ${argv.name}, Port: ${argv.port})`);
    // argv.nameとargv.portはdemandOptionによりundefinedにならないことが保証される
    await serverProxy.connect(argv.name, argv.port);

    console.log('Starting agent');
    const agent = new Agent();
    serverProxy.setAgent(agent);

    await agent.start(argv.load_memory, argv.init_message ?? null, argv.count_id);
  } catch (error: unknown) {
    // TypeScriptの厳格なエラーハンドリング（errorはデフォルトでunknown）
    console.error('Failed to start agent process:');
    if (error instanceof Error) {
      console.error(error.message);
      console.error(error.stack);
    } else {
      console.error(String(error));
    }
    process.exit(1);
  }
})().catch((error: unknown) => {
  console.error('Unexpected error in agent process:');
  if (error instanceof Error) {
    console.error(error.message);
    console.error(error.stack);
  } else {
    console.error(String(error));
  }
  process.exit(1);
});
