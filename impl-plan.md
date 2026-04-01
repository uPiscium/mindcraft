# 実装計画: `src/` の Mineflayer 以外を Python 化する

## 目的

- `src/` 配下のうち、Mineflayer 依存を除いた処理を Python に移行する。
- 既存の動作を壊さず、段階的に確認しながら置き換える。
- 最終的に JS 側は Mineflayer の接続・操作層に寄せ、Python 側を制御本体にする。

## 移行方針

- まず純粋関数や I/O が少ない処理から移す。
- 1 フェーズごとに「実装 → 単体確認 → 起動確認」を行う。
- 既存 API/プロトコルはできるだけ維持し、変更は後ろ倒しにする。
- 置換対象と残置対象の境界を最初に固定する。

## 現状の整理

- JS に残す候補: Mineflayer 本体に密接な `src/agent/` の一部。
- Python 化する候補: `src/mindcraft/`, `src/process/`, `src/models/`, `src/utils/` の Mineflayer 非依存部分。
- つなぎ役: JS の Mineflayer bot と Python の制御層を RPC / Socket / HTTP で接続する。

## フェーズ 1: 境界を固定する

### 目的

- どのファイルを Python に移すかを明確にする。
- JS 側の責務を「ゲーム接続」に限定する。

### 作業

- `src/` 配下を Mineflayer 依存 / 非依存で分類する。
- 依存の薄い順に移行優先度を付ける。
- 既存の入出力と責務を簡単な一覧にする。

### 検証

- 移行対象一覧に抜けがないか確認する。
- 変更せずに現状の起動経路を把握する。

### 完了条件

- 移行対象が決まっている。
- JS 残置範囲が明確になっている。

## フェーズ 2: Python の土台を作る

### 目的

- Python 側の実行基盤を用意する。

### 作業

- `pyproject.toml` を作る。
- Python のエントリポイントを作る。
- 設定読み込みとログ出力の共通基盤を作る。

### 推奨構成

- `FastAPI` + `Uvicorn` + `pydantic` + `httpx`

### 検証

- Python サービスが起動することを確認する。
- 最小の健康確認エンドポイントを用意する。

### 完了条件

- Python 側が単独起動できる。
- JS なしでも設定を読み込める。

## フェーズ 3: 設定と共通ユーティリティを移す

### 目的

- まず副作用の少ない部分を Python 化する。

### 作業

- `settings.js` 相当を Python の設定クラスへ移す。
- `src/utils/text.js` のような文字列整形を移植する。
- 必要なら `src/utils/math.js`, `src/utils/examples.js` も順次移す。

### 検証

- 同じ入力に対して JS と Python の出力が一致することを確認する。
- 文字列整形系の単体テストを用意する。

### 完了条件

- 設定とユーティリティが Python で使える。
- 既存挙動との差分がない。

## フェーズ 4: モデル層を移す

### 目的

- LLM クライアント群を Python に寄せる。

### 作業

- `src/models/ollama.js` を最初に移植する。
- その後、共通インターフェースを決めて他モデルを順次移す。
- エラー処理、タイムアウト、レスポンス正規化を統一する。

### 検証

- `ollama` の送信・応答整形が一致するか確認する。
- モデルごとの最小テストを追加する。

### 完了条件

- Python からモデル API を叩ける。
- 少なくとも `ollama` で回帰がない。

## フェーズ 5: プロセス管理を移す

### 目的

- 起動・監視・再起動ロジックを Python 側へ移す。

### 作業

- `src/process/agent_process.js` の責務を整理する。
- 当面は Mineflayer 本体の起動は JS に残してもよい。
- Python が再起動条件や停止制御を管理する形に寄せる。

### 検証

- 起動失敗・再起動・停止が期待通り動くか確認する。
- シグナル処理が壊れていないか確認する。

### 完了条件

- プロセス制御の主導権が Python にある。

## フェーズ 6: サーバ / 制御面を移す

### 目的

- `mindserver` 相当の制御層を Python に統合する。

### 作業

- `src/mindcraft/mindserver.js` を Python 実装に置換する。
- UI や既存クライアントとの互換性を優先する。
- Socket.IO を維持するか、別の通信方式にするか決める。

### 検証

- 既存 UI が接続できることを確認する。
- エージェント一覧・状態更新が正しく反映されることを確認する。

### 完了条件

- 制御サーバが Python で動く。
- 既存の利用フローが壊れない。

## フェーズ 7: `src/agent/` の非 Mineflayer 部分を移す

### 目的

- 会話制御、記憶、タスク管理などを Python 側へ寄せる。

### 作業

- Mineflayer 依存のある部分を除外しながら移植する。
- 会話管理、プロンプト生成、状態管理を Python に集約する。
- Mineflayer に触る箇所だけ JS に残す。

### 検証

- エージェントの振る舞いが大きく変わらないことを確認する。
- 重要なタスクフローを 1 つずつ再確認する。

### 完了条件

- JS 側の `src/agent/` は薄いラッパーになっている。

## フェーズ 8: JS を薄いアダプタに縮小する

### 目的

- 最終的に JS を Mineflayer 専用の接続層へ縮める。

### 作業

- `main.js` を Python 起動用の薄い入口にする。
- `src/process/init_agent.js` を必要最小限に整理する。
- 可能なら JS 側の設定やルーティングも削る。

### 検証

- 既存の起動コマンドが引き続き使えることを確認する。
- 失敗時のメッセージが分かりやすいことを確認する。

### 完了条件

- Python が制御本体、JS が Mineflayer 接続層という構造になっている。

## 段階的な確認方法

- 各フェーズで単体テストを 1 本追加または更新する。
- 各フェーズで最小起動確認を 1 回行う。
- 可能なら JS と Python の出力比較テストを作る。
- 変更範囲が広がる前に、1 機能ずつ切り替える。

## 進める順番のおすすめ

1. `src/utils/` の純粋関数
2. `src/models/ollama.js`
3. `settings.js` と設定読み込み
4. `src/process/` の制御
5. `src/mindcraft/` のサーバ制御
6. `src/agent/` の非 Mineflayer 部分
7. JS の縮小と最終整理

## リスク

- 通信境界が曖昧だとデバッグが難しくなる。
- UI や既存スクリプトとの互換性が崩れる可能性がある。
- Mineflayer 依存の切り分けを誤ると移植コストが増える。

## 最初の着手点

- まず `utils/text.js` と `models/ollama.js` を Python 化する。
- その後に `settings.js` と起動フローを移す。

## 進捗状況

- [x] フェーズ 1: 境界整理
- [x] フェーズ 2: Python 土台作成
- [x] フェーズ 3: `utils` / 設定 / プロフィール移行
- [x] フェーズ 4: `ollama` 移行と実接続
- [ ] フェーズ 5 以降: プロセス管理・mindserver・agent 移行
- [x] `main.js` は TOML プロフィール読み込みに対応済み
- [x] `src/models/ollama.js` と `mindcraft_py/models/ollama.py` に `<think>` 安定化処理を追加済み

## 完全移行に向けた残タスク

- Python に `mindserver` 相当を実装する
- エージェント状態管理を Python 主導にする
- UI と状態更新の通信層を Python へ寄せる
- `src/mindcraft/mindcraft.js` を薄い互換層にする
- `src/process/*` の JS 実装を最小ブリッジにする
- 最後に JS 側の Mineflayer 非依存ロジックを削除する

## JS に残す線引き

- Mineflayer に直結する接続・操作処理
- Minecraft サーバ接続の最小アダプタ
- 既存 UI との一時的な互換ラッパー
- Node でしか扱えない外部連携の最終ブリッジ

## Python に寄せる対象

- 設定読み込み
- 起動 CLI
- プロセス監視と再起動
- コマンド解釈とプロンプト整形
- モデル呼び出し
- 状態管理とイベント集約

## 完全移行の実装順

1. `src/process/agent_process.js` を最小ブリッジに固定する
2. `src/mindcraft/mindcraft.js` の起動・停止・再起動を Python 側イベントに寄せる
3. Python に `mindserver` 相当の状態 API を作る
4. UI が見ているエージェント状態を Python から返す
5. `src/agent/` の Mineflayer 非依存部を Python 化する
6. JS の Mineflayer 依存以外を段階的に削除する

## 実装メモ

- 既存の CLI とプロフィール読み込みはそのまま使える
- 再起動ロジックは Python 側の `AgentProcess` を中心にする
- JS 側は「接続するだけ」に寄せるほど後工程が楽になる

## 現在の到達点

- `settings.js` / `main.js` は TOML プロフィール前提で動く
- `mindcraft_py/cli.py` はポート衝突を自動回避する
- `mindcraft_py/agent_process.py` が再起動条件を保持している
- `src/process/create_agent_process.js` は分岐を1箇所に集約している
- `src/mindcraft/mindcraft.js` は agent 生成の配線のみを担当している

## 次の一手

- `mindserver` の状態管理 API を Python 側へ寄せる
- `startAgent` / `stopAgent` / `destroyAgent` を Python イベントに置き換える
- `src/mindcraft/mindcraft.js` の状態保持をさらに削る

## 現在の進捗

- [x] `MindcraftRuntime` に agent 登録/更新/取得 API を追加
- [x] `README.py.md` に Python 側の状態 API を追記
- [x] JS の agent 状態管理を `src/mindcraft/agent_registry.js` に分離
- [ ] JS の `mindserver` から表示以外の状態管理を完全に切り離す
- [ ] `createAgent` / `destroyAgent` / `startAgent` / `stopAgent` の最終実装を Python 側イベントに寄せる
- [x] Python 側に `MindserverState` レジストリを追加
- [x] JS 側の agent process 参照を `agent_registry.js` に寄せた
