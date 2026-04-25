# Task Pool Execution Loop Integration - 実フロー自動接続

## 目的

`MindcraftRuntime` に接続済みの task pool を、実際のエージェント実行フローに自動で組み込む．
この段階では、task の手動取得/返却ではなく、エージェントの起動・実行・停止に合わせて task を自動的に消費・完了・返却する．

## 対象範囲

- エージェント起動時の task 初期化
- 実行開始前の task 取得
- task 取得直後の self-prompt 自動開始
- 実行成功時の task 完了
- 完了直後の次 task 自動取得
- 実行失敗時の task 返却
- 停止・切断・異常終了時の task 回収
- current task の状態表示

## 境界

- Python 側は task の管理・選択・状態遷移を保持する
- JS 側は Mineflayer の実行と self-prompt を担当する
- 自動起動や次 task への遷移は JS の実行ループで行い、task の正本は Python に置く

## 接続方針

### 1. 起動時に task を注入する

- `MindcraftRuntime.load_task_pool_file()` で読み込んだ task を runtime に保持する
- エージェント起動時に該当 task 群を task pool に登録する
- 同一 task の二重登録は避ける
- `profile.task_pool_file` / `settings.task_pool_file` / CLI 引数のいずれかから読み込み可能にする

### 2. 実行開始前に task を取得する

- エージェントが行動を開始する直前に `acquire_task_for_agent()` を呼ぶ
- 取得した task は agent state の `current_task` に保持する
- 取得した task は `self_prompter` にも注入し、自動プロンプトループを開始する
- task が取得できない場合は待機・再試行・終了のいずれかに分岐する

### 3. 成功時に task を完了する

- 行動が正常終了したら `complete_task_for_agent()` を呼ぶ
- `complete_task()` は task を `COMPLETED` にする
- 完了後は `current_task` をクリアする
- 完了後に次 task があればそのまま自動取得して `_activateTask()` へ渡す

### 4. 失敗時に task を返却する

- 行動失敗やモデル失敗時は `yield_task_for_agent()` を呼ぶ
- 失敗理由を `history` に残す
- 返却後は `current_task` をクリアする

### 5. 停止・切断時に task を回収する

- `stop_agent()` / `destroy_agent()` / `shutdown()` でロック中 task を回収する
- エージェントの crash や disconnect でも task が LOCKED のまま残らないようにする

### 6. task 状態を可視化する

- `list_tasks()` で task pool の状態を確認できるようにする
- agent state に `current_task` を載せる
- UI やログから、今どの task を実行中か追えるようにする

## 実行時の流れ

1. エージェント起動
2. task file 読み込み
3. task pool 登録
4. 行動開始前に task を acquire
5. エージェントの実処理を実行
6. 成功なら complete、失敗なら yield
7. 次の task を acquire

## 失敗時の扱い

- task 取得失敗: 待機またはスキップ
- task 実行失敗: `yield_task_for_agent()` で返却
- task 完了前の例外: `finally` で回収
- 切断/終了: `shutdown` / `stop` の経路で回収

## 仕様テスト

### `tests/test_runtime_task_pool_integration.py`

- 起動時に task file が読み込まれる
- 実行開始前に task が取得される
- 成功時に task が COMPLETED になる
- 失敗時に task が AVAILABLE に戻る
- 停止時に LOCKED task が残らない

### `tests/test_agent_process.py`

- エージェント停止・再起動時に current task が破損しない
- 例外経路でも task 回収が走る

## 非対象

- task 定義フォーマットの再設計
- task pool file loader の再設計
- 分散キュー化
- 永続化

## 【実装メモ】

- `src/agent/tasks/task_pool.js` に task pool の実体を配置済み．
- `src/agent/agent.js` で起動時の acquire，idle 時の acquire，成功時の complete，失敗/中断時の yield を接続済み．
- `src/agent/self_prompter.js` で current task を prompt に注入し，自動起動できるようにしている．
- `src/agent/action_manager.js` で action 成功/失敗フックを受け，task lifecycle に伝播している．
- `src/agent/library/full_state.js` で current task を状態表示している．
- `main.js` と `mindcraft_py/runtime.py` 側の `task_pool_file` 読み込みと連携済み．
- 参照 ADR は `ADR/0003-task-pool-execution-loop.md`．
- 回帰テストは `tests/test_runtime_task_pool_integration.py`、`tests/test_task_slot_orchestration.py`、`tests/test_self_prompter.js`、`tests/test_agent_task_handoff.js` にある．
