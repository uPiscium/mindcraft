# Task Slot Orchestration - エージェント内タスクスロット

## 目的

エージェントに「現在実行中の task を保持する slot」を持たせ、slot に task が入っている間は task execution controller を起動して最後まで実行する．
将来的には、この slot への task 注入をエージェント自身が task pool から自発的に行う形へ移行する．

## 背景

- task pool は既にある
- task file loader もある
- BFS runner と task execution controller もある
- しかし、task の取得と task の実行をつなぐ「中間の居場所」がまだ弱い

## 概念

### Task Slot

- エージェントごとに 1 つだけ持つ
- 現在実行中または実行予定の task を保持する
- controller は slot が空でなければ実行する
- slot が空なら controller は動かない

## 役割分担

### Task Pool

- task を供給する
- 依存関係と available 状態を管理する

### Task Slot

- エージェントが今やる task を保持する
- task の状態を `EMPTY / ASSIGNED / RUNNING / COMPLETED / FAILED` で表す

### TaskExecutionController

- slot に入った task を最後まで実行する
- 成功なら complete
- 失敗なら yield

## 状態遷移

- `EMPTY` -> `ASSIGNED`
- `ASSIGNED` -> `RUNNING`
- `RUNNING` -> `COMPLETED`
- `RUNNING` -> `FAILED`
- `FAILED` -> `EMPTY` (返却後)
- `COMPLETED` -> `EMPTY` (解放後)

## 実行フロー

1. エージェントが slot の空きを確認する
2. slot が空なら task pool から task を取得する
3. 取得した task を slot に格納する
4. controller が slot の task を実行する
5. 実行成功なら complete して slot を空にする
6. 実行失敗なら yield して slot を空にする
7. 次の task があれば繰り返す

## 将来像

- 現在: `task pool -> slot -> controller`
- 将来: `agent -> task pool -> slot -> controller`

## 設計方針

- slot は 1 つだけにする
- slot の状態は明示的に持つ
- slot が空のとき controller は何もしない
- stop / disconnect / shutdown で slot を必ず回収する
- 自発的取得は slot への注入処理だけを差し替えればよいようにする

## 推奨コンポーネント

### `TaskSlot`

- 役割: エージェントの現在 task を保持する
- フィールド例: `state`, `task`, `last_reason`, `updated_at`

### `TaskSlotManager`

- 役割: slot の状態遷移を管理する
- 入力: task / complete / failed / empty
- 出力: 更新後の slot

### `TaskOrchestrator`

- 役割: slot と controller と task pool をつなぐ
- slot が空なら acquire
- slot が埋まっていれば controller 実行

## 仕様テスト

### `tests/test_task_slot_orchestration.py`

- slot が空のとき controller は動かない
- task が slot に入ると controller が起動する
- 成功時に slot が空になる
- 失敗時に slot が空になる
- stop / disconnect 時に slot が回収される

## 非対象

- task 定義フォーマットの変更
- task pool file loader の変更
- BFS runner の廃止
- Mineflayer 実行の全面置換

## 【実装メモ】

- `mindcraft_py/task_slot.py` に `TaskSlot` / `TaskSlotManager` を追加済み．
- `mindcraft_py/task_slot_orchestrator.py` に slot を見て controller を起動する orchestrator を追加済み．
- `mindcraft_py/runtime.py` に agent ごとの slot 参照を追加済み．
- `mindcraft_py/task_execution_controller.py` は assigned task を slot から実行できるように拡張済み．
- 回帰テストは `tests/test_task_slot_orchestration.py` にある．
- 参照 ADR は `ADR/0007-task-slot-orchestration.md`．
