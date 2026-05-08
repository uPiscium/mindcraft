
ランタイムフロー

概要
- このリポジトリは Mindcraft エージェントフレームワークを提供します。実行時は主に2つのランタイムに分かれます。
  - Node.js 側エントリ（main.js）：MindServer（Web UI + socket.io）を起動し、エージェントプロセスを管理します。
  - Python 側ラッパ（mindcraft_py/__main__.py -> cli.py）：Node の起動をラップし、タスクプール読み込みなど Python 側の補助機能を提供します。

エントリポイント
- Node（main.js）
  - CLI 引数（--profiles, --task_path, --task_id）と環境変数を解析します。
  - 必要に応じてタスクファイルを読み `settings.task` を設定します。
  - `Mindcraft.init(...)` を呼び出し、各プロファイルについて `Mindcraft.createAgent(settings)` を実行します。

- Python（mindcraft_py.__main__, mindcraft_py.cli）
  - `mindcraft-py` CLI は Node コマンド（main.js の実行）を組み立て、空いている MindServer ポートを解決してから Node を起動します。
  - `--task_pool_file` が指定された場合、Python 側でタスクプールを読み込み `TASK_POOL_JSON` を環境変数にセットして Node を起動します。
  - Python 側の `MindcraftRuntime` はタスク管理やテスト用ユーティリティとして動作します。

主要コンポーネント
- src/mindcraft/mindcraft.js（Node）
  - MindServer を生成する薄いブリッジです。top-level の main.js から利用されます。
  - `createAgent(settings)` はエージェント登録とプロセス生成を行います。

- src/mindcraft/mindserver.js（Node）
  - Express + Socket.IO による中央サーバ（MindServer）。Web UI をホストし、クライアントとエージェントプロセス間のメッセージを仲介します。
  - 主な socket イベント：create-agent, login-agent, run-query-command, run-action-command, listen-to-agents など。

- src/mindcraft/agent_registry.js（Node） / mindcraft_py/mindserver_state.py（Python）
  - エージェントのメタ情報（settings, viewer_port, socket, in_game, process, full_state）を保持するシンプルなインメモリレジストリです。

- mindcraft_py/runtime.py -> MindcraftRuntime（Python）
  - Python 側のランタイム抽象。エージェントレジストリ（MindserverState）、Node ランタイム起動ラッパ（NodeRuntimeProcess）、AgentProcess 管理、タスクプール（CentralTaskCoordinator）を持ちます。
  - 主要メソッド：init, create_agent, start_agent_process, create_agent_process, load_task_pool_file, register_task(s), acquire_task, complete_task。

- mindcraft_py/node_runtime.py -> NodeRuntimeProcess（Python）
  - Node 実行のラッパ。`node main.js` を spawn して Node 側ランタイムを起動します。

- mindcraft_py/agent_process.py, python_agent_process.py, src/mindcraft/node_agent_process.js
  - Python 側の `PythonAgentProcess` はテストや埋め込み用の軽量プロセス抽象です。
  - `NodeAgentProcess`（JS）は実際に子プロセスを spawn して `src/process/init_agent.js` を実行します。
  - Python の `AgentProcess` は NodeRuntimeProcess と組み合わせて統一的な start/stop API を提供します。

エージェント起動シーケンス（代表的な流れ）
1. ユーザーが `node main.js --profiles <p>` または `python -m mindcraft_py --profiles <p>` を実行します。
2. `main.js` が `Mindcraft.init(...)` を呼んで MindServer を起動し、各プロファイルに対して `Mindcraft.createAgent(settings)` を呼びます。
3. `Mindcraft.createAgent(settings)`（src/mindcraft/mindcraft.js）:
   - プロファイル名の検証
   - `registerAgent(settings, viewer_port)` でエージェントを登録
   - `createAgentProcess(agentName, mindserverPort, settings)` を呼んでプロセスインスタンスを取得
   - `agentProcess.start(...)` を呼んでエージェントプロセスを起動
4. Node のエージェントプロセス（NodeAgentProcess.start）は `node src/process/init_agent.js -n <name> -p <port> ...` を spawn します。
5. `src/process/init_agent.js`（エージェントプロセスのエントリ）:
   - `serverProxy.connect(name, port)` で MindServer に接続
   - `new Agent()` を生成して `serverProxy.setAgent(agent)` を呼ぶ
   - `agent.start(...)` を呼んでモデルアダプタやメモリのロード、初期プロンプトなどを処理してエージェントループを開始
6. 接続後は socket.io を通じて MindServer と `get-full-state`, `run-query-command`, `run-action-command`, `chat-message` 等のイベントをやり取りします。

エージェントのライフサイクル操作
- `startAgent(agentName)`（JS）: プロセスを再起動（forceRestart）します。
- `stopAgent(agentName)`（JS）: プロセスを停止し registry の in_game を false にします。
- `destroyAgent(agentName)`（JS）: プロセスを停止してエージェントを registry から削除します。
- Python 側の MindcraftRuntime も同等のメソッドを提供しています（start_agent_process, restart_agent_process, stop_agent_by_name, destroy_agent, mark_agent_exited）。

MindServer の主な socket.io イベント（抜粋）
- create-agent(settings, callback): 設定検証 → `mindcraft.createAgent(settings)` を呼び成功/失敗を返す。
- login-agent(agentName): エージェントを in_game にし、そのソケットを設定する。
- connect-agent-process(agentName): エージェントプロセス側が自らのソケットを登録するために呼ぶ。
- run-query-command / run-action-command: 外部クライアントから来たコマンドを該当エージェントのソケットに転送し応答を受け取る。
- listen-to-agents: UI が定期的な状態アップデートを要求。MindServer はログイン中の各エージェントに対して `get-full-state` を問い合わせ、1秒ごとに `state-update` をブロードキャストする。

MC サーバ補助（src/mindcraft/mcserver.js）
- LAN 上の Minecraft サーバ探索や ping（findServers, serverInfo, getServer）を行うヘルパ群。settings による自動検出時に利用されます。

設定と環境変数
- Node 側 main.js が参照する主な環境変数：
  - `MINECRAFT_PORT`, `MINDSERVER_PORT`, `PROFILES` (JSON 配列), `INSECURE_CODING`, `BLOCKED_ACTIONS` (JSON), `MAX_MESSAGES`, `NUM_EXAMPLES`, `LOG_ALL`, `TASK_POOL_JSON`。
- Python の `mindcraft-py` は Node 実行前に `MINDSERVER_PORT` を設定し、必要なら `TASK_POOL_JSON` をセットします。

シーケンス要約（簡潔）
- `node main.js` または `python -m mindcraft_py` を実行すると MindServer が起動し、各プロファイルにつきエージェントプロセスが生成されます。
- エージェントプロセスは MindServer に接続して socket.io 経由で状態やコマンドをやり取りします。

参照ポイント
- 主要 Node ファイル: `main.js`, `src/mindcraft/mindserver.js`, `src/mindcraft/mindcraft.js`, `src/process/*`, `src/agent/*`。
- 主要 Python ファイル: `mindcraft_py/runtime.py`, `mindcraft_py/cli.py`, `mindcraft_py/node_runtime.py`, `mindcraft_py/agent_process.py`。
- タスクプールは Python 側で管理される設計（CentralTaskCoordinator）。必要に応じて `TASK_POOL_JSON` で Node 側へ渡せます。

次の候補（要望があれば実施します）
1. エージェント起動パスのシーケンス図（PlantUML など）を作成する。
2. socket.io イベントの送受信ペイロードを全て一覧化する。
3. ドキュメント内に該当関数や行番号への詳細な参照を追加する。
