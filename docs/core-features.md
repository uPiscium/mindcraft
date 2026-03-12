# Mindcraft コア機能まとめ

このドキュメントは、このリポジトリの「中核機能」を、**目的**・**役割**・**実装方法**の観点で整理したものです。
実装参照先は主に `main.js` と `src/` 配下です。

## 1. 起動・設定統合（CLI + 環境変数）

- 目的: 実験実行やローカル運用時に、同じコードで柔軟に起動条件を切り替える。
- 役割: プロファイル指定、単一タスク実行、実行時上書き設定を一元的に受け付ける。
- 実装方法:
  - `main.js` で `yargs` により `--profiles`, `--task_path`, `--task_id` を解釈。
  - `settings.js` の既定値をベースに、`MINECRAFT_PORT` / `PROFILES` / `INSECURE_CODING` など環境変数で上書き。
  - 各プロファイル JSON を読み込み、`Mindcraft.createAgent(...)` を繰り返して複数エージェントを生成。
- 主な実装: `main.js`, `settings.js`

## 2. MindServer（制御ハブ + Web UI + API）

- 目的: 複数エージェントを統合管理し、外部UI/外部クライアントから操作可能にする。
- 役割:
  - エージェント状態の集約（在席/接続/ビューアポートなど）。
  - Socket.IO 経由で作成・再起動・停止・破棄・シャットダウンを提供。
  - 静的Web UI配信と状態ストリーミング。
- 実装方法:
  - `express` + `http` + `socket.io` でサーバを構築。
  - `registerAgent` で接続情報を保持し、`agents-status` を購読者へ配信。
  - `listen-to-agents` 時に 1秒間隔で `get-full-state` を各エージェントへ要求。
- 主な実装: `src/mindcraft/mindserver.js`

## 3. エージェントプロセス管理（分離・自動再起動）

- 目的: 1エージェントの異常が全体へ波及しないよう、実行単位を分離する。
- 役割: 子プロセス起動、停止、ハング時の強制再起動、終了コードに応じた制御。
- 実装方法:
  - `AgentProcess` が `node src/process/init_agent.js ...` を `spawn`。
  - 異常終了時に一定条件で再起動（短時間クラッシュは再起動抑制）。
  - `SIGINT` で正常停止、`forceRestart()` で応答待ちつき再起動。
- 主な実装: `src/process/agent_process.js`, `src/process/init_agent.js`

## 4. Minecraft サーバ探索・バージョン検証

- 目的: LAN/指定ポート運用の双方で接続成功率を上げる。
- 役割: サーバ検出、`minecraft-protocol` での ping、対応バージョン判定。
- 実装方法:
  - `port=-1` のとき `49000..65000` を走査し、最初の有効サーバを採用。
  - サーバ応答のバージョン文字列から数値バージョンを抽出。
  - サポート対象外・期待バージョン不一致時に明示的エラー。
- 主な実装: `src/mindcraft/mcserver.js`, 呼び出し元 `src/mindcraft/mindcraft.js`

## 5. エージェント中核ループ（対話・行動・イベント）

- 目的: LLM応答とゲーム内アクションを連続的に接続し、タスク達成まで走らせる。
- 役割:
  - 発話受信 -> 履歴保存 -> 応答生成 -> コマンド解釈 -> 実行。
  - スポーン後初期化（Vision, Task, event handler, modes）。
  - 終了条件判定（タスク達成・タイムアウト・切断）。
- 実装方法:
  - `Agent.start()` が主要コンポーネント（`Prompter`, `History`, `ActionManager` など）を初期化。
  - `handleMessage()` でコマンド入り応答をパースし `executeCommand()` 実行。
  - 300ms周期の update で mode / self-prompt / task判定を更新。
- 主な実装: `src/agent/agent.js`

## 6. コマンドDSL（!command）と実行基盤

- 目的: LLM出力を安全なインターフェースでゲーム操作へ変換する。
- 役割: 構文解析、型チェック、ドメインチェック、アクション/クエリ実行。
- 実装方法:
  - `!name(arg1, ...)` 形式を正規表現で抽出。
  - パラメータ型（int/float/boolean/ItemName等）を検証。
  - `actionsList` / `queryList` を統合した `commandMap` から実行。
  - `blacklistCommands()` でタスクごとの無効化を適用。
- 主な実装: `src/agent/commands/index.js`, `src/agent/commands/actions.js`, `src/agent/commands/queries.js`

## 7. アクション実行制御（割り込み・タイムアウト・再開）

- 目的: 非同期行動の競合や無限ループを抑制し、安定実行する。
- 役割: 実行排他、停止要求、タイムアウト、resume action 管理。
- 実装方法:
  - `ActionManager.runAction()` が単一アクション実行を直列化。
  - 実行中は `stop()` で掘削/移動/PvPを中断し安全停止。
  - 高頻度反復を検知して `cancelResume()`、最悪時 `cleanKill()`。
- 主な実装: `src/agent/action_manager.js`

## 8. 自律モード（Reactive Behavior）

- 目的: LLM指示待ちでは遅い危険回避や定常行動を常時補完する。
- 役割: 自己保全、スタック解除、戦闘/逃走、アイテム回収、たいまつ設置など。
- 実装方法:
  - `modes_list` に優先順モードを定義し、毎tick更新。
  - 各モードは割り込み可否を持ち、`execute(...)` 経由で ActionManager 実行。
  - 中断発生時は AUTO MESSAGE で再計画を促す。
- 主な実装: `src/agent/modes.js`

## 9. マルチエージェント会話オーケストレーション

- 目的: 複数Bot間で会話衝突を抑えつつ協調作業を成立させる。
- 役割: 会話セッション開始/終了、受信キュー、応答タイミング制御、切断監視。
- 実装方法:
  - ConversationManager が active conversation を単一管理。
  - busy状態に応じて短/長ディレイで返信スケジューリング。
  - 他Botとの送受信は `mindserver_proxy` 経由で中継。
- 主な実装: `src/agent/conversation.js`, `src/agent/mindserver_proxy.js`

## 10. 長期メモリ・履歴管理

- 目的: コンテキスト上限を超える会話でも方針連続性を維持する。
- 役割: 直近履歴保持、古い履歴の要約、永続化、再起動復元。
- 実装方法:
  - `History.turns` が短期履歴、閾値超過で `promptMemSaving()` により要約更新。
  - `bots/<agent>/memory.json` に memory / turns / self_prompt 状態を保存。
  - full history を別ファイルに追記して追跡可能にする。
- 主な実装: `src/agent/history.js`

## 11. LLM層（モデル抽象化 + 例示選択 + プロンプト組立）

- 目的: 複数プロバイダに跨って同一エージェント体験を提供する。
- 役割:
  - API自動判定/モデルインスタンス生成。
  - 会話/コーディング/ビジョン/埋め込みモデルの分離運用。
  - コマンドDoc・スキルDoc・例示を埋め込んだテンプレート置換。
- 実装方法:
  - `_model_map.js` で `prefix` ベースの動的ロード。
  - `Prompter` が `$COMMAND_DOCS`, `$CODE_DOCS`, `$EXAMPLES` 等を展開。
  - `Examples` が embedding 類似度（失敗時は語彙重なり）で few-shot 選択。
- 主な実装: `src/models/_model_map.js`, `src/models/prompter.js`, `src/utils/examples.js`, `src/models/*.js`

## 12. スキルライブラリ（Minecraft 操作プリミティブ）

- 目的: 複雑な行動を再利用可能な低レベル関数群として統一する。
- 役割: 移動、採掘、クラフト、製錬、建築、戦闘、インベントリ操作など。
- 実装方法:
  - `skills.js` に Mineflayerベースの実動作を集約。
  - `mcdata.js` がアイテム/ブロック知識、レシピ、Bot初期プラグインを提供。
  - `skill_library.js` が `!newAction` 用に関連スキルDocを選別して提示。
- 主な実装: `src/agent/library/skills.js`, `src/utils/mcdata.js`, `src/agent/library/skill_library.js`

## 13. タスクフレームワーク（Crafting/Cooking/Construction）

- 目的: 研究・評価向けに課題を標準化し、スコアリングを自動化する。
- 役割: 初期インベントリ配布、ゴール設定、タスク進行、完了判定。
- 実装方法:
  - `Task` が task_type ごとに validator を切替。
  - `CookingTaskInitiator` がワールドをコマンドで準備。
  - `ConstructionTaskValidator` + `Blueprint` がブロック一致率を算出。
  - 完了時に `Task ended with score : ...` を履歴へ記録。
- 主な実装: `src/agent/tasks/tasks.js`, `src/agent/tasks/cooking_tasks.js`, `src/agent/tasks/construction_tasks.js`

## 14. 画像理解と可視化

- 目的: テキストだけで不足する視覚情報を補う。
- 役割: スクリーンショット解析、視点制御、ブラウザ一人称ビュー提供。
- 実装方法:
  - `VisionInterpreter` が座標/プレイヤー方向を見て画像を取得。
  - 取得画像を vision model へ渡し、分析テキストを返す。
  - `render_bot_view` が有効なら `prismarine-viewer` をポート公開。
- 主な実装: `src/agent/vision/vision_interpreter.js`, `src/agent/vision/browser_viewer.js`

## 15. 自動コード生成 (`!newAction`) とサンドボックス実行

- 目的: 既存コマンドで表現しづらい新規行動を実行可能にする。
- 役割: LLM生成コードの検証・隔離実行・結果要約。
- 実装方法:
  - `!newAction` は `allow_insecure_coding` 有効時のみ実行。
  - `Coder` がコードブロック抽出 -> ESLint検査 -> SES compartment実行。
  - 公開APIを `skills`, `world`, `Vec3`, `log` に制限し、割り込みフラグ対応。
- 主な実装: `src/agent/commands/actions.js`, `src/agent/coder.js`, `src/agent/library/lockdown.js`

## 補足: このリポジトリの設計意図（全体）

- 研究用途での再現性と運用性を重視し、**複数エージェント**・**複数タスク**・**複数モデル**を同一基盤で扱えるようにしている。
- 生成AIの自由度（`!newAction`）と、安全側の実行管理（モード/割り込み/プロセス分離）を併存させている。
- タスク評価の仕組みを内蔵し、実行ログから自動スコアリングまで繋がるワークフローを提供している。
