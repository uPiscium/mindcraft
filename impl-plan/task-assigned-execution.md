# Task Assigned Execution - 割当済みタスクの自動実行

## 目的

task pool から割り当てられた task を、受け取り後に自動で実行し、完了または返却まで進める仕組みを設計する．
この段階では「task を選ぶ」ではなく、「割り当てられた task をどう実行するか」に焦点を当てる．

## 背景

- task pool と task file loader は既に存在する
- BFS runner により依存順の追従実行はできる
- しかし、task を受け取った後に、その内容を元に実際の行動へ変換して最後まで進める専用機構はまだない

## 対象範囲

- task 受領後の実行開始
- task 内容の解釈
- 実行計画の生成
- 実行中の状態保持
- 成功時の完了処理
- 失敗時の返却処理
- 中断・切断時の回収

## 非対象

- task の選択ロジックそのもの
- BFS / 自発的取得の切り替えロジック
- task 定義フォーマットの変更
- task pool file loader の変更
- Mineflayer の全面移植

## 設計方針

### 1. task は「実行対象」として扱う

- 取得した task は `current_task` として保持する
- task の `payload` を実行要求として解釈する
- task は「何をやるか」を表し、実行器は「どうやるか」を決める

### 2. 実行は段階的に進める

- task 受領
- task 実行計画生成
- step 実行
- 成功なら complete
- 失敗なら yield

### 3. 実行器は task ごとに差し替え可能にする

- task ごとの executor を切り替えられるようにする
- デフォルト executor は payload をそのまま自然言語指示として扱う
- 将来的に task 種別ごとの専用 executor を追加できるようにする

## 推奨コンポーネント

### `TaskExecutionController`

- 役割: 割当済み task の実行フローを管理する
- 入力: runtime, agent, current task
- 出力: 実行結果

### `TaskExecutor`

- 役割: task を実際の行動ステップへ変換する
- 入力: task entity
- 出力: step 列または実行結果

### `TaskExecutionPlan`

- 役割: task の実行順序と完了条件を保持する
- 例: `collect`, `craft`, `place`, `report`

## 実行フロー

1. task が割り当てられる
2. controller が current task を受け取る
3. executor が payload を解釈して plan を生成する
4. plan の各 step を既存の action loop に流す
5. step が成功したら次へ進む
6. 全 step が完了したら task を complete する
7. step が失敗したら task を yield する

## 状態遷移

- `AVAILABLE` -> `LOCKED` -> `COMPLETED`
- `AVAILABLE` -> `LOCKED` -> `AVAILABLE` (失敗/返却)

## エラー処理

- task payload の解釈に失敗した場合は yield
- step 実行で例外が出た場合は yield
- 実行途中で agent が停止した場合は回収
- 依存不足の task はそもそも execution 対象に入れない

## インターフェース案

### `TaskExecutionController.run(task)`

- 役割: task を最後まで実行する
- 出力: `{ success, reason, steps }`

### `TaskExecutor.plan(task)`

- 役割: task payload から step plan を作る
- 出力: 実行ステップの配列

### `TaskExecutor.executeStep(step)`

- 役割: 1 step を既存 action loop に流す
- 出力: 成功/失敗

## 連携先

- `mindcraft_py/runtime.py`
- `mindcraft_py/task_runner.py`
- `src/agent/agent.js`
- `src/agent/action_manager.js`
- `src/agent/self_prompter.js`

## 仕様テスト

### `tests/test_task_execution_controller.py`

- task が plan に変換される
- plan の step が順番に実行される
- step 失敗時に yield される
- task 完了時に complete される

### `tests/test_task_runner.py`

- BFS runner から controller に接続できる
- 依存順に task が流れたあと実行される

## 段階的導入

### Phase 1

- task payload を自然言語のまま executor に渡す
- 1 task = 1 execution unit として扱う

### Phase 2

- task 種別ごとの planner を追加する
- `collect` / `craft` / `build` のような step 化を進める

### Phase 3

- BFS runner を自発的取得に置き換える
- controller は「割当済み task の実行」だけを担う

## 【実装メモ】

- `mindcraft_py/task_execution_controller.py` に `TaskExecutionController` を追加済み．
- `TaskExecutionController` は `acquire -> plan -> executeStep -> complete/yield` の最小フローを担う．
- `mindcraft_py/task_runner.py` から controller を利用できるようにしている．
- 既存の BFS runner は依存追従の実行経路として残している．
- 回帰テストは `tests/test_task_execution_controller.py` と `tests/test_task_runner.py` にある．
- 参照 ADR は `ADR/0006-task-assigned-execution-controller.md`．
