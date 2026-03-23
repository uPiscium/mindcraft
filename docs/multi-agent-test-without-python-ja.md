# Pythonを使わずにマルチエージェントのタスクテストを実行する手順

この手順は、`tasks/run_task_file.py` などのPythonスクリプトを使わずに、Node.jsのみでマルチエージェントのタスクを実行する方法です。

## 前提

- Node.js v18またはv20
- Minecraft Java Edition（ローカルでLAN公開できる状態）
- APIキー設定済みの `keys.json`

## 1) 依存関係をインストール

```bash
npm install
```

## 2) APIキーを設定

`keys.example.json` を `keys.json` にコピーし、利用するプロバイダのAPIキーを設定します。

## 3) Minecraftワールドを起動

- シングルプレイのワールドを起動
- LANに公開
- 公開ポートを控える（例: `55916`）

## 4) 接続先を `settings.js` で確認

`settings.js` の以下を実環境に合わせます。

- `host`（通常は `localhost`）
- `port`（LAN公開したポート）
- `auth`（ローカル検証なら通常 `offline`）

## 5) マルチエージェントタスクを実行

このリポジトリには `tasks/multiagent_crafting_tasks.json` があり、`agent_count: 2` のタスクをそのまま実行できます。

### 例1: shearsタスク

```bash
node main.js --task_path tasks/multiagent_crafting_tasks.json --task_id multiagent_techtree_1_shears
```

### 例2: wooden_pickaxeタスク

```bash
node main.js --task_path tasks/multiagent_crafting_tasks.json --task_id multiagent_techtree_1_wooden_pickaxe
```

## 補足

- `--task_path` を使う場合、`--task_id` は必須です。
- Pythonなしで単発タスクを回す用途にはこの方法が最短です。
- 複数タスクを連続実行したい場合は、シェルスクリプトやPowerShellで上記コマンドを順番に呼び出してください。
