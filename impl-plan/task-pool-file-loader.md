# Task Pool File Loader - 依存付きタスク定義の読込

## 目的

`MindcraftRuntime` の task pool に対して、依存関係や優先度を含む複数タスクをファイルから読み込めるようにする．
既存の `main.js` の task file 形式は使わず、この機能専用の新しい定義形式を採用する．

## ファイル形式

- 形式: TOML
- 構造: 配列形式 `[[tasks]]`
- 1ファイルに複数 task を定義できる
- 依存関係は `depends_on = ["task-id", ...]` で表現する

### 例

```toml
[[tasks]]
id = "gather_oak_logs"
payload = "Collect at least four logs"
priority = 1

[[tasks]]
id = "craft_planks"
payload = "Craft planks after logs are ready"
depends_on = ["gather_oak_logs"]
priority = 2
```

## タスク定義ルール

- `id` は必須
- `payload` は必須
- `depends_on` は省略可能
- `priority` は省略可能
- `state` / `lock_metadata` / `history` はファイルでは定義しない
- ファイル読込時は `AVAILABLE` として登録する

## 公開API

### `MindcraftRuntime.load_task_pool_file(task_file_path)`

- 役割: TOML task file を読み込み、runtime の task pool に登録する
- 入力: ファイルパス
- 出力: 登録された task の一覧
- 振る舞い:
  - ファイルを読み込む
  - `[[tasks]]` 配列を parse する
  - 各 task を `register_tasks()` 経由で登録する
  - 既存 task は id 単位で上書きする

### `MindcraftRuntime.register_tasks(tasks)`

- 役割: 複数 task をまとめて登録する
- 入力: task 配列
- 出力: 登録結果の配列

## 実行フローとの接続

- 起動時に profile または CLI から task file を指定できるようにする
- task file はエージェント起動前または起動直後に読み込む
- task pool へ登録後、`acquire_task_for_agent()` から通常フローに接続する

## エラー処理

- ファイルが存在しない場合は明示的に失敗する
- TOML parse エラーは起動失敗として扱う
- `id` / `payload` が不足する task は拒否する
- 依存先 task が存在しない場合は登録時に失敗するか、起動時に検証エラーとして止める

## 仕様テスト

### `tests/test_runtime_task_file_loader.py`

- TOML task file を読み込める
- `[[tasks]]` が複数登録される
- `depends_on` が保存される
- `priority` が保存される
- 不正な task file はエラーになる

## 非対象

- 既存の `main.js` task file 形式の拡張
- JSON / YAML 対応
- 永続化
- 分散キュー化
