# 実装完了項目

- `mindcraft_py/task_coordinator.py`
  - 中央タスク管理機構 `CentralTaskCoordinator` を実装
  - `AcquireTask` 相当のアトミックな取得処理を実装
  - `YieldTask` 相当の返却処理と履歴追記を実装
  - ロックタイムアウトの解放処理を実装
  - `depends_on` を持つタスク依存を扱えるようにした
  - capability レベルによる絞り込みは削除した

- `mindcraft_py/environment.py`
  - `TranslateSpatialData` を実装
  - `FilterInventoryByContext` を実装

- `mindcraft_py/llm_gateway.py`
  - `GenerateAction` 相当のスキーマ付き生成ゲートウェイを実装
  - JSON パース失敗時の再試行ループを実装

- `mindcraft_py/runtime.py`
  - `CentralTaskCoordinator` を runtime に接続
  - `register_task` / `list_tasks` / `acquire_task` / `yield_task` を公開
  - `shutdown()` でタスクプールをクリア

- `src/agent/tasks/task_pool.js`
  - エージェント側の task pool 実体を実装

- `src/agent/self_prompter.js`
  - current task を prompt に注入できるようにした

- `src/agent/action_manager.js`
  - action 成功/失敗フックを通じて task lifecycle を連携

- `src/agent/agent.js`
  - 起動時の acquire と idle 時の自動取得を接続
  - 成功時 complete / 失敗・中断時 yield を接続

- `src/agent/library/full_state.js`
  - `currentTask` を state に表示

- `main.js`
  - `task_pool_file` を CLI から受け取って読み込むようにした

- `mindcraft_py/task_execution_controller.py`
  - 割当済み task を実行する controller を実装
  - task の acquire / plan / execute / complete / yield を扱う

- `mindcraft_py/__init__.py`
  - 上記モジュールの主要シンボルを再エクスポート

- テスト
  - `tests/test_runtime_task_pool.py`
  - `tests/test_task_coordinator.py`
  - `tests/test_environment_helpers.py`
  - `tests/test_llm_gateway.py`
  - `tests/test_task_coordinator_unit.py`
  - `tests/test_runtime_task_pool_unit.py`
  - `tests/test_runtime_task_pool_integration.py`
  - `tests/test_runtime_task_file_loader.py`
  - `tests/test_task_pool_loader.js`
  - `tests/test_task_execution_controller.py`
  - `tests/test_task_runner.py`

- 検証
  - `pytest` 全 47 件通過
