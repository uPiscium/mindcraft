# 実装完了項目

- `mindcraft_py/task_coordinator.py`
  - 中央タスク管理機構 `CentralTaskCoordinator` を実装
  - `AcquireTask` 相当のアトミックな取得処理を実装
  - `YieldTask` 相当の返却処理と履歴追記を実装
  - ロックタイムアウトの解放処理を実装

- `mindcraft_py/environment.py`
  - `TranslateSpatialData` を実装
  - `FilterInventoryByContext` を実装

- `mindcraft_py/llm_gateway.py`
  - `GenerateAction` 相当のスキーマ付き生成ゲートウェイを実装
  - JSON パース失敗時の再試行ループを実装

- `mindcraft_py/__init__.py`
  - 上記モジュールの主要シンボルを再エクスポート

- テスト
  - `tests/test_task_coordinator.py`
  - `tests/test_environment_helpers.py`
  - `tests/test_llm_gateway.py`

- 検証
  - `just check` 通過
  - `pytest` 全 60 件通過
