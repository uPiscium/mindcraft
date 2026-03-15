# mindcraft (Python Runtime Guide)

このドキュメントは、既存の`README.md`とは別に、Python主体でmindcraftを実行するためのガイドです。

## 何がPython版か

- 起動フローと制御はPython（`main.py`, `mindcraft_py/`）で実行します。
- Minecraft接続・mineflayer・botの実行はJavaScript側（既存実装）を利用します。
- PythonはNode.jsブリッジを起動し、MindServer（Socket.IO）経由でエージェントを操作します。

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

### 3) Python依存を同期

```bash
uv sync
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
- `--profiles`, `--task_path`, `--task_id` はPython版でも利用できます。
- 環境変数オーバーライド（`MINECRAFT_PORT`, `MINDSERVER_PORT` など）も既存仕様と互換です。
- 設定解決は`src/mindcraft-py/resolve-settings.js`（Node側）で実施します。

## 主要ファイル

- `main.py`: Python版CLIエントリ
- `mindcraft_py/runner.py`: 起動フロー（設定解決→profile読込→agent作成→待機）
- `mindcraft_py/runtime.py`: Node起動・MindServer接続・create-agent呼び出し
- `mindcraft_py/config.py`: Nodeブリッジ経由で設定JSONを取得
- `src/mindcraft-py/init-mindcraft.js`: MindServer起動
- `src/mindcraft-py/resolve-settings.js`: CLI/envを含む設定解決

## よくある問題

- `Cannot find package 'yargs'`
  - Node依存未導入です。`npm install`を実行してください。
- `No module named socketio` などPython依存エラー
  - `uv sync`を再実行してください。
- Minecraftに接続できない
  - `settings.js`の`host`/`port`/`auth`、LAN公開ポート、Minecraftバージョンを確認してください。

## セキュリティ注意

- `allow_insecure_coding`を有効化すると、モデルによるコード生成・実行が可能になります。
- 公開サーバ接続時はリスクを理解した上で利用し、必要ならDocker運用を推奨します。
