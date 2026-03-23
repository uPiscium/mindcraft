# mindcraft (Python Runtime Guide)

このドキュメントは、既存の`README.md`とは別に、Python主体でmindcraftを実行するためのガイドです。

## 何がPython版か

- 起動フローと制御はPython（`main.py`, `mindcraft_py/`）で実行します。
- Minecraft接続・mineflayer・botの実行はJavaScript側（既存実装）を利用します。
- PythonはNode.jsブリッジを起動し、MindServer（Socket.IO）経由でエージェントを操作します。
- 設定解決はPython側へ移しており、LLM向けコマンド仕様もPython側へ段階的に移行中です。
- Python版の設定は `settings.toml` を優先し、無ければ `settings.js` を読みます。

## 前提条件

- Minecraft Java Edition（ローカルワールドをLAN公開、または接続先サーバを用意）
- Node.js（v18 or v20 LTS推奨）
- Python（3.11以上）
- `uv`（Python依存管理）
- 利用するLLM向けAPIキー（`keys.json`）

## セットアップ

### 1) Node依存をインストール

```bash
npm install
```

### 2) uvをインストール

未導入の場合は公式手順に従ってインストールしてください。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Nix環境を使う場合は、`flake.nix` に `just` も含めてあります。

```bash
nix develop
```

### 3) Python依存を同期

```bash
uv sync
```

開発用ツールも入れる場合は以下を利用します。

```bash
uv sync --group dev
```

### 4) APIキーを設定

`keys.example.json`を`keys.json`にリネームし、利用するプロバイダのキーを設定します。

## クイックスタート

MinecraftワールドをLAN公開した状態で、以下を実行します。

```bash
uv run python main.py --profiles ./agents/Andy.json
```

## 実行方法

### Pythonエントリ

```bash
uv run python main.py
```

### プロファイル指定

```bash
uv run python main.py --profiles ./agents/Andy.json ./agents/Bob.json
```

### タスク指定

```bash
uv run python main.py --task_path tasks/basic/single_agent.json --task_id gather_oak_logs
```

### モジュール実行

```bash
uv run python -m mindcraft_py --profiles ./agents/Andy.json
```

## Python API利用

```python
import json

from mindcraft_py import create_agent, init, wait

init(port=8080, host_public=True, auto_open_ui=True)

with open('./agents/Andy.json', 'r', encoding='utf-8') as f:
    profile = json.load(f)

create_agent({'profile': profile})
wait()
```

サンプルは`src/mindcraft-py/example.py`も参照してください。

## 設定の扱い

- 基本設定は既存の`settings.js`を使用します。
- Python版は `settings.toml` を優先して読みます。無い場合のみ `settings.js` を使います。
- `--profiles`, `--task_path`, `--task_id` はPython版でも利用できます。
- 環境変数オーバーライド（`MINECRAFT_PORT`, `MINDSERVER_PORT` など）も既存仕様と互換です。
- 設定解決は`mindcraft_py/config.py`で実施し、`settings.js`をPython側で読み取ります。

## Pythonコマンド基盤の現状

- `mindcraft_py/commands.py` に、Python側の command registry の最小実装があります。
- 現時点では `!stats`, `!inventory`, `!nearbyBlocks`, `!entities`, `!stop`, `!goal`, `!newAction` の仕様をPython側で管理しています。
- `mindcraft_py/js_command_specs.py` で `src/agent/commands/actions.js` と `src/agent/commands/queries.js` から仕様を抽出し、Python側定義との自動比較に使っています。
- `mindcraft_py/commands.py` では、`!craftable`, `!modes`, `!savedPlaces`, `!checkBlueprint*`, `!getBlueprint*`, `!getCraftingPlan`, `!searchWiki`, `!help` も Python registry に取り込んでいます。
- `mindcraft_py/actions.py` / `mindcraft_py/commands.py` / `mindcraft_py/runtime.py` の組み合わせで、query/action の bridge を共通化しています。
- `mindcraft_py/catalog.py` が Python registry から command catalog を生成し、JS 側の command docs 供給元としても使われます。
- query 系の一部は Python registry から MindServer 経由で JavaScript 実行アダプタを呼べるようになっています。
- mineflayer を使う実処理本体は引き続きJavaScript側ですが、query 実行入口は Python から呼び出せます。
- `mock_client` を有効にすると、Minecraft を起動せずに mock agent で query bridge をテストできます。

## Profile の形式

- Python版では `agents/*.json` と `agents/*.toml` の両方を読み込めます。
- `profiles/*.json` も同様に TOML 化できます。
- まずは JSON を残したまま、必要な profile だけ TOML に置き換える運用でも問題ありません。

## 主要ファイル

- `main.py`: Python版CLIエントリ
- `mindcraft_py/runner.py`: 起動フロー（設定解決→profile読込→agent作成→待機）
- `mindcraft_py/runtime.py`: Node起動・MindServer接続・create-agent呼び出し
- `mindcraft_py/config.py`: `settings.js`とCLI/envオーバーライドをPython側で解決
- `mindcraft_py/commands.py`: Python側の command registry、コマンド docs 生成、引数パース
- `mindcraft_py/js_command_specs.py`: JavaScript側コマンド仕様の抽出と比較用ローダー
- `src/mindcraft-py/init-mindcraft.js`: MindServer起動
- `src/agent/mindserver_proxy.js`: Pythonからの query 実行要求を受ける JavaScript 側アダプタ
- `src/mindcraft/mindserver.js`: query 実行要求の中継
- `src/process/mock_agent_client.js`: Minecraft なしで接続できる mock agent client
- `tests/test_python_commands.py`: Python command registry のテスト
- `tests/test_mock_query_bridge.py`: mock client を使った query bridge の統合テスト
- `tests/test_multiagent_inventory_init.py`: multi-agent タスクの初期インベントリ確認
- `justfile`: Python向けのテスト・lint・format コマンド

## よくある問題

- `Cannot find package 'yargs'`
  - Node依存未導入です。`npm install`を実行してください。
- `No module named socketio` などPython依存エラー
  - `uv sync`を再実行してください。
- Minecraftに接続できない
  - `settings.js`の`host`/`port`/`auth`、LAN公開ポート、Minecraftバージョンを確認してください。

## テストと整形

```bash
uv run --group dev pytest
uv run --group dev ruff check .
uv run --group dev ruff format .
```

現在のPythonテストは `tests/test_python_commands.py` にあり、以下を確認します。

- コマンド文字列のパース
- 引数型変換とドメイン検証
- command docs 生成
- Python側で管理しているデフォルトコマンド仕様の回帰チェック
- JavaScript側 `src/agent/commands/*.js` との自動比較
- Python query bridge のユニットテスト
- mock client を使った、Minecraft 非起動時の query bridge 統合テスト

`just`を使う場合は以下でも実行できます。

```bash
just test
just lint
just fmt
just check
```

## セキュリティ注意

- `allow_insecure_coding`を有効化すると、モデルによるコード生成・実行が可能になります。
- 公開サーバ接続時はリスクを理解した上で利用し、必要ならDocker運用を推奨します。
