# Task Pool BFS Runner - 依存追従実行器

## 目的

task pool に登録された task を、依存関係の順に BFS 的にたどって自動実行する Python 側の runner を用意する．
この runner は、将来的な自発的 task 取得に置き換えるための中間レイヤーとして機能する．

## 役割

- 依存関係が解けた task を優先して実行する
- 実行結果に応じて `complete / yield` を行う
- 実行順を明示的に返す
- 依存未解決の task を可視化する

## 入力

- `MindcraftRuntime`
- `requester_id`
- `executor(task)` 関数

## 処理方針

### 1. 依存グラフを作る

- `depends_on` から task 間の依存関係を構築する
- 依存先が完了していない task は実行対象にしない

### 2. 実行順を決める

- 依存が解けた task を ready queue に入れる
- ready queue は priority と id で安定ソートする
- ready queue から 1 件ずつ取り出して実行する

### 3. 実行結果で状態遷移する

- 成功なら `complete_task_by_id` 相当で `COMPLETED`
- 失敗なら `yield_task` で `AVAILABLE` に戻す
- 例外なら `yield` して停止するか継続するかを選べるようにする

### 4. 依存先を解放する

- 完了した task を起点に依存先の未解決集合を更新する
- 依存先がすべて解けた task を ready queue に追加する

## 仕様

### `run_dependency_bfs(runtime, requester_id, executor, stop_on_failure)`

- 役割: 依存順に task を自動実行する
- 出力: executed / completed / failed / unresolved の一覧
- 振る舞い:
  - ready な task から順に実行する
  - 成功時は task を complete する
  - 失敗時は task を yield する
  - `stop_on_failure=False` の場合は次の ready task へ進める

## デモ

### `scripts/task_pool_bfs_demo.py`

- `tasks/task_pool_demo.toml` を読み込む
- BFS 順に task を acquire / complete する
- 依存チェーンが順に解決されることを出力する

## テスト

### `tests/test_task_runner.py`

- 依存順に task が実行される
- 失敗時に `yield` と `unresolved` が返る

## 非対象

- task の自発的取得ロジックそのもの
- Mineflayer 実行の全面変更
- task 定義フォーマットの変更
