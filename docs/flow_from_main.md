開始点: main.js を node で起動したときの処理フロー

以下は main.js をエントリとして実行されたときに起こる主要な処理を時系列順に並べたものです。各ステップは「ファイル: 関数/処理 — 説明」の形式で記載します。

1) main.js: スクリプト開始 / parseArguments()
   - main.js が起動し CLI 引数を parseArguments()（yargs）で解析します。
   - 解析結果により settings オブジェクトのいくつかの値（profiles, task, ports 等）を更新します。

2) main.js: 環境変数の適用
   - main.js が process.env を読み、settings の一部（MINECRAFT_PORT, MINDSERVER_PORT, PROFILES, など）を上書きします。

3) main.js -> src/mindcraft/mindcraft.js: init(true, settings.mindserver_port, settings.auto_open_ui)
   - Mindcraft.init(host_public, port, auto_open_ui)
   - 内部で createMindServer(host_public, port) を呼び出します（次ステップ）。auto_open_ui が true ならブラウザを自動で開く試みを行います。

4) src/mindcraft/mindserver.js: createMindServer(host_public, port)
   - express と http サーバ、socket.io をセットアップし、public ディレクトリを静的配信します。
   - socket.io の接続ハンドラを登録して、API イベント（create-agent, get-settings, login-agent, chat-message, restart-agent, stop-agent, destroy-agent, shutdown, bot-output, listen-to-agents 等）を処理します。
   - createMindServer はリッスンを開始しサーバインスタンスを返します（Mindcraft.init が保持）。

5) main.js: 各 profile に対して Mindcraft.createAgent(settings) を呼ぶ（ループ）
   - main.js は profiles 配列を走査し各 profile JSON を読み、settings.profile にセットして Mindcraft.createAgent(settings) を呼びます。

6) src/mindcraft/mindcraft.js: createAgent(settings)
   - settings.profile.name が存在するか検査します。
   - settings をディープコピーし、内部で viewer_port を決め、registerAgent(settings, viewer_port) を呼んで MindServer 側の agent メタデータを予約します。
   - mcserver.getServer(host, port, minecraft_version) を試験的に呼んで Minecraft サーバ情報を取得し（失敗しても継続）、AgentProcess を new し start() を呼びます。

7) src/mindcraft/mindserver.js: registerAgent(settings, viewer_port)
   - AgentConnection オブジェクトを作成して agent_connections[agentName] に格納します（後で Socket 経由で接続されたときに参照されます）。

8) src/process/agent_process.js: new AgentProcess(name, mindserver_port) / start(load_memory, init_message, agentIndex)
   - AgentProcess.start() が呼ばれ、node コマンドで子プロセスを spawn します。起動コマンドは `node src/process/init_agent.js <name> -n <name> -c <count_id> -p <mindserver_port> ...` の形式です。
   - 子プロセスの stdout/stderr は 'inherit' で親プロセスに接続されます。
   - 子プロセスの exit イベントを監視し、エラー条件や短時間での終了時は再起動や親プロセス終了を行います。

9) 子プロセス: src/process/init_agent.js が実行される
   - init_agent.js は CLI 引数を yargs でパースし、serverProxy.connect(name, port) を呼んで MindServer に接続します。

10) src/agent/mindserver_proxy.js: serverProxy.connect(name, port)
   - socket.io-client を使って `http://localhost:<port>` に接続します。
   - 接続成功後、'get-settings' イベントでサーバからエージェント設定を要求し、受け取った設定を setSettings() で反映します。
   - 接続イベントや agents-status, chat-message, restart-agent などの socket イベントハンドラを登録します。
   - 接続後、サーバへ 'connect-agent-process' 相当の通知を送ることで MindServer 側でこの子プロセス接続を知らせます。

11) init_agent.js: Agent を生成して起動
   - const agent = new Agent()（src/agent/agent.js）を実行し、serverProxy.setAgent(agent) で proxy 側に保存します。
   - await agent.start(load_memory, init_message, count_id) を呼んでエージェント本体を起動します。

12) src/agent/agent.js: Agent.start(load_mem, init_message, count_id)
   - 名前取得（Prompter）と validateNameFormat を行う。
   - コンポーネント初期化: History, Coder, NPCController, MemoryBank, SelfPrompter, ActionManager, Prompter, ConversationManager などを生成・初期化する。
   - 履歴をロードする場合はその復元を行う（load_mem フラグ）。
   - this.task = new Task(this, settings.task, taskStart) を作る。
   - this.bot = initBot(this.name) を呼んで Minecraft ボットインスタンス（mineflayer 等）を生成する。

13) Agent.start: ボットのイベントバインド
   - bot.once('kicked'), bot.once('end'), bot.on('error') などで接続失敗や切断を扱う。
   - initModes(this) を呼んでモード群を初期化する。
   - bot.on('login') ハンドラ内で serverProxy.login() を呼んで MindServer 側へログイン通知を送る。

14) Agent.start: spawn タイムアウトと spawn ハンドラ
   - spawn が一定時間来ない場合にタイムアウトで終了する仕組みが設定される（settings.spawn_timeout）。
   - bot.once('spawn', ...) が呼ばれると:
     - addBrowserViewer(this.bot, count_id) を呼びブラウザビューア（必要なら）を登録
     - this.vision_interpreter = new VisionInterpreter(this, settings.allow_vision) を初期化
     - this._setupEventHandlers(save_data, init_message) を呼んでチャット/whisper ハンドラ等を準備
     - this.startEvents() を呼んで定期 update ループと各種イベントハンドラを開始
     - タスクが指定されている場合は this.task.initBotTask() と this.task.setAgentGoal() を呼ぶ

15) Agent._setupEventHandlers(save_data, init_message)
   - whisper と chat の受信ハンドラ（respondFunc）を登録し、受信メッセージを handleMessage() に渡す
   - セルフプロンプトの復元や初期メッセージ（init_message）処理を行う

16) Agent.startEvents() と update ループ
   - bot の time/health/death/messagestr/idle 等のイベントをハンドルするコールバックを登録する
   - NPC コントローラを初期化し、一定間隔（INTERVAL）で this.update(delta) を呼ぶ永続ループを開始する

17) メッセージ受信時の流れ: Agent.handleMessage(source, message)
   - 受信されたメッセージを翻訳（handleEnglishTranslation / handleTranslation）して履歴に追加
   - containsCommand(message) でコマンド検出。コマンドであれば commandExists を確認し、executeCommand(this, message) を呼ぶ
   - コマンドでなければ Prompter.promptConvo(histroy) を呼んで応答を生成し、routeResponse() で送信
   - 実行結果（execute_res）は履歴に保存され、必要に応じて bot によるアクション（ActionManager 経由）を起こす

18) コマンド実行の下流: commands -> ActionManager -> bot
   - executeCommand()（./agent/commands/index.js）はエージェントの状態とコマンドを解釈し、ActionManager に命令を渡す場合がある
   - ActionManager は bot の API（採掘、移動、道具操作 など）を使って実際のゲーム内アクションを実行する

19) MindServer 側との双方向連携
   - Agent は sendOutputToServer(this.name, message) で bot の出力やチャットを MindServer に送る
   - MindServer は UI や外部クライアントからの操作（restart-agent, stop-agent, destroy-agent, send-message 等）を受け、対応する socket イベントを child process に中継したり、mindcraft モジュールを通じて親プロセスに指示を出す

20) エージェント終了・再起動の流れ
   - 子プロセス（AgentProcess 内の spawn したプロセス）が exit すると、AgentProcess の exit ハンドラが呼ばれ logoutAgent(this.name) を行う
   - exit のコードやシグナルに応じて AgentProcess は再起動を試みたり、親プロセスを終了させる
   - Mindcraft.destroyAgent(name) を呼ぶと、親プロセス側で agent_processes から削除し stop() を呼ぶなどの後処理を行う

21) シャットダウン経路
   - MindServer に対する 'shutdown' イベントまたは Agent.killAll() により、サーバは全エージェントを停止させ、数秒後にプロセスを終了する

補足: 主要ファイルと主要関数の役割（参考）
 - main.js: CLI 解析と Mindcraft.init / Mindcraft.createAgent の起点
 - src/mindcraft/mindcraft.js: MindServer 作成と AgentProcess の生成管理（高レベルオーケストレータ）
 - src/mindcraft/mindserver.js: socket.io ベースの中央サーバ。UI と外部 API の窓口
 - src/process/agent_process.js: 各エージェントを子プロセスとして spawn し監視する
 - src/process/init_agent.js: 子プロセス内のエントリ。MindServer に接続して Agent を起動する
 - src/agent/agent.js: エージェントの主体。ボットの生成、イベントハンドリング、プロンプト/コマンド処理、タスク管理を行う

ファイル出力

このファイルは docs/flow_from_main.md としてプロジェクトに追加しました。

追加の要望:
- より詳細に "handleMessage -> Prompter -> executeCommand -> ActionManager -> bot の API 呼び出し" を追ってコード行まで示すことも可能です。
- Graphviz によるシーケンス図を生成することも可能です。

終了
