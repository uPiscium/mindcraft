概要

このドキュメントは Mindcraft プロジェクトの実行時エントリポイントと呼び出しフローを日本語でまとめたものです．各エントリについて，ファイル名，エントリ関数(または主要な処理)，呼び出し先のファイルと関数，及び主要関数の簡単な説明を記載しています．

1) Node CLI エントリ: main.js

- ファイル: main.js
- エントリ: `node main.js` で実行されるトップレベルスクリプト
- 主な処理:
  - parseArguments(): yargs で CLI 引数(profiles, task_path, task_id 等)を解析する
  - 引数に従い settings を更新し，Mindcraft.init() と Mindcraft.createAgent() を呼び出す

- 呼び出し先:
  - src/mindcraft/mindcraft.js :: init(host_public, port, auto_open_ui)
  - src/mindcraft/mindcraft.js :: createAgent(settings)(profiles ごとに呼び出す)

- 備考: profile JSON と(あれば)task JSON を読み，MindServer を起動して各エージェントのプロセスを作成します．

2) 高レベル制御: src/mindcraft/mindcraft.js

- ファイル: src/mindcraft/mindcraft.js
- エクスポート関数(外部から呼ばれる実行エントリ):
  - init(host_public=false, port=8080, auto_open_ui=true)
    - createMindServer(host_public, port) を呼んで MindServer(web + socket)を作成する
    - numStateListeners() が 0 の場合はブラウザ UI を自動で開く
  - createAgent(settings)
    - settings.profile.name の検証
    - registerAgent(settings, viewer_port) で MindServer 側にエージェント情報を登録
    - mcserver.getServer(...) を試行して Minecraft サーバ情報を解決(任意)
    - AgentProcess を生成し agentProcess.start(...) で子プロセスを起動
  - getAgentProcess, startAgent, stopAgent, destroyAgent, shutdown などのユーティリティ

- 主な呼び出し先:
  - ./mindcraft/mindserver.js :: createMindServer, registerAgent, numStateListeners
  - ../process/agent_process.js :: AgentProcess
  - ./mcserver.js :: getServer

3) MindServer(中央サーバ): src/mindcraft/mindserver.js

- ファイル: src/mindcraft/mindserver.js
- エクスポート関数:
  - createMindServer(host_public=false, port=8080)
    - express と http サーバ，socket.io を設定し静的ファイルを配信する
    - socket イベントハンドラを登録(create-agent, get-settings, login-agent, chat-message, restart-agent, stop-agent, destroy-agent, shutdown, bot-output, listen-to-agents 等)
    - 'create-agent' 時に settings_spec を検証し mindcraft.createAgent(settings) を呼ぶ
  - registerAgent(settings, viewer_port)
    - AgentConnection オブジェクトを作成して agent_connections に登録する(エージェントのメタデータ保持)
  - logoutAgent(agentName)
  - getIO(), getServer(), numStateListeners()

- 重要な内部ヘルパー:
  - agentsStatusUpdate(socket): 現在のエージェント一覧を 'agents-status' で送信
  - addListener(listener_socket) / removeListener(listener_socket): listener 管理と定期的な full state 取得ループ

4) エージェントプロセスマネージャ: src/process/agent_process.js

- ファイル: src/process/agent_process.js
- クラス: AgentProcess
- 機能:
  - constructor(name, port)
  - start(load_memory=false, init_message=null, count_id=0)
    - node src/process/init_agent.js を引数付きで spawn して子プロセスを立ち上げる
    - 子プロセスの exit / error を監視し，必要なら再起動またはプロセス終了を行う
  - stop(): 子プロセスに SIGINT を送り停止させる
  - forceRestart(): 停止後に再起動を試みる

- 直接的な呼び出し先／影響:
  - spawn により src/process/init_agent.js が実行される
  - 子が exit したら logoutAgent(this.name) を呼ぶ

5) 子プロセスのエントリ: src/process/init_agent.js

- ファイル: src/process/init_agent.js
- 振る舞い: 各エージェント用の子プロセスで実行されるスクリプト
- 流れ:
  - CLI 引数(name, load_memory, init_message, count_id, port 等)を解析
  - serverProxy.connect(name, port) で MindServer に接続
  - new Agent() で Agent インスタンスを生成し serverProxy.setAgent(agent) を呼ぶ
  - agent.start(load_memory, init_message, count_id) を実行してボットを起動

- 呼び出し先:
  - ../agent/agent.js :: Agent.start
  - ../agent/mindserver_proxy.js :: serverProxy.connect, setAgent

6) エージェント実行本体: src/agent/agent.js

- ファイル: src/agent/agent.js
- クラス: Agent
- 主要メソッド・振る舞い:
  - async start(load_mem=false, init_message=null, count_id=0)
    - History, Coder, VisionInterpreter, Prompter, ActionManager, NPCController, MemoryBank, SelfPrompter 等を初期化
    - 名前チェック(validateNameFormat)を行い，this.task = new Task(...) を設定
    - this.bot = initBot(this.name) で Minecraft ボットを生成し，'login','spawn','kicked','end','error' などのイベントをバインド
    - spawn イベント発火時に addBrowserViewer，VisionInterpreter の初期化，_setupEventHandlers，startEvents を呼び，タスク目標を設定
  - async _setupEventHandlers(save_data, init_message)
    - whisper/chat の受信ハンドラや自動食事設定，セルフプロンプト状態の復元，初期メッセージ送信などを行う
  - startEvents(): 定期アップデートループ(update)，time/health/death/messagestr/idle 等のイベント登録，NPC 初期化
  - async handleMessage(source, message, max_responses=null)
    - メッセージ受信の主要処理．コマンド検出，翻訳，履歴追加，Prompter による応答生成，executeCommand 実行，routeResponse による応答送出を行う
  - routeResponse / openChat: 他エージェントやゲームチャット，MindServer へ応答を送る
  - update(delta), checkTaskDone(), cleanKill(), killAll() などの補助処理

- 参照している主なモジュール:
  - ../agent/history.js, ../agent/coder.js, ../agent/vision/vision_interpreter.js
  - ../models/prompter.js, ../agent/modes.js, ../utils/mcdata.js
  - ./commands/index.js, ./action_manager.js, ./npc/controller.js, ./memory_bank.js, ./self_prompter.js
  - ./conversation.js, ../utils/translator.js, ./vision/browser_viewer.js, ./mindserver_proxy.js

7) MindServer クライアントプロキシ: src/agent/mindserver_proxy.js

- ファイル: src/agent/mindserver_proxy.js
- クラス: MindServerProxy(シングルトン．exported as serverProxy)
- 主な機能:
  - connect(name, port): socket.io-client で MindServer に接続，各種イベントを登録し 'get-settings' で設定を取得して setSettings を呼ぶ
  - setAgent(agent): このプロセスの Agent インスタンスを保存してコールバックに使う
  - login(), shutdown(): MindServer に対応するイベントを送信
  - getFullState ハンドラ: MindServer がエージェントのフル状態を要求したときに応答する
  - sendBotChatToServer / sendOutputToServer: サーバへ出力を emit するユーティリティ

- 参照先:
  - socket.io-client, ../agent/conversation.js, ./library/full_state.js, ./settings.js など

8) その他の注目モジュール(簡潔)

- src/mindcraft/mcserver.js
  - getServer(host, port, minecraft_version): Minecraft サーバ情報を解決して返す．Mindcraft.createAgent の中で呼ばれる．

- src/agent/vision/vision_interpreter.js
  - VisionInterpreter: 視覚情報(スクリーンショット等)の解釈を担う．spawn 時に生成される．

- src/agent/commands/index.js
  - containsCommand, commandExists, executeCommand, isAction, truncCommandMessage, blacklistCommands 等を提供．Agent.handleMessage から実行される．

- src/agent/library/full_state.js
  - getFullState(agent): Web UI 向けにエージェントの状態を集約して返す．MindServer のリスナーが利用する．

- src/agent/history.js, action_manager.js, npc/*, models/*
  - Agent の振る舞いを支える補助モジュール群．詳細は各ファイルを参照してください．

標準的な起動シーケンス(要約)

1. ユーザが `node main.js --profiles path/to/profile.json` を実行する
2. main.js が引数を解析し，settings を更新して Mindcraft.init(...) を呼ぶ
3. Mindcraft.init が MindServer を作成し(必要なら UI を自動オープン)リッスンを開始する
4. main.js は各 profile ごとに Mindcraft.createAgent(settings) を呼ぶ
   - MindServer に agent のメタデータを登録(registerAgent)
   - AgentProcess を生成し start() を呼び `node src/process/init_agent.js` を spawn
5. spawn された子プロセスは init_agent.js を実行し，serverProxy.connect() で MindServer に接続してから Agent インスタンスを生成し agent.start() を呼ぶ
6. Agent.start() が Minecraft ボット(initBot)を生成，spawn 後に vision とイベントループを設定してチャット応答やタスク処理を開始する

付録: 主要ファイル -> 主要関数(エントリ)対応表

- main.js -> parseArguments(), Mindcraft.init(), Mindcraft.createAgent()
- src/mindcraft/mindcraft.js -> init(), createAgent(), startAgent(), stopAgent(), destroyAgent(), shutdown()
- src/mindcraft/mindserver.js -> createMindServer(), registerAgent(), logoutAgent(), agentsStatusUpdate(), addListener/removeListener
- src/process/agent_process.js -> AgentProcess.start()/stop()/forceRestart()(init_agent.js を spawn)
- src/process/init_agent.js -> serverProxy.connect(), new Agent(), agent.start()
- src/agent/agent.js -> Agent.start(), _setupEventHandlers(), startEvents(), handleMessage(), update(), cleanKill(), killAll()
- src/agent/mindserver_proxy.js -> MindServerProxy.connect(), setAgent(), login(), shutdown(), sendOutputToServer()
