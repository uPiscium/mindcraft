# Python 利用手順

このリポジトリでは、Python を中核にしつつ、既存の JS MindServer UI を可視化層として使えます。

## 前提

- Python 3.11 以上
- `uv` か `pip`
- Minecraft サーバが `localhost:30000` で起動済み
- Ollama サーバが `https://ollama-melchior.arc.upiscium.dev` で起動済み

## セットアップ

```bash
uv sync
```

`uv` を使わない場合は、少なくともテスト実行に必要な依存を入れてください。

## プロフィール

- プロフィールは `agents/*.toml` を使います。
- 代表例は `agents/Andy.toml` です。
- JSON は使いません。

## 最小の実行例

```python
from pathlib import Path

from mindcraft_py.commands import execute_query
from mindcraft_py.profiles import load_profile
from mindcraft_py.runtime import MindcraftRuntime

root = Path(__file__).resolve().parent
profile = load_profile(root / "agents" / "Andy.toml")

runtime = MindcraftRuntime()
runtime.init(port=8080, host_public=False, auto_open_ui=False)

settings = {
    "host": "localhost",
    "port": 30000,
    "auth": "offline",
    "mock_client": True,
    "blocked_actions": [],
    "profile": profile,
}

runtime.create_agent(settings)
print(execute_query(runtime, profile["name"], "!stats"))
runtime.shutdown()
```

## CLI から起動する

```bash
python -m mindcraft_py --profiles ./agents/Andy.toml
```

インストール後は以下でも起動できます。

```bash
mindcraft-py --profiles ./agents/Andy.toml
```

タスクを指定する場合は、必要に応じて次のようにします。

```bash
mindcraft-py --task_path ./tasks/basic/single_agent.json --task_id gather_oak_logs
```

If port `8080` is already occupied, the Python CLI will try the next free port.
You can still override it explicitly with `MINDSERVER_PORT`.
The chosen port is printed on startup.

Python 側でプロセスを制御したい場合は `mindcraft_py.runtime.MindcraftRuntime` の
`start_agent_process()` / `stop_agent()` / `restart_agent()` を使います。

## 現在の到達点

- Python 側に runtime / state / process の土台が揃っています。
- JS の MindServer は UI / Socket.IO の可視化層として残しています。
- `agents/*.toml` を起点に、`mindcraft_py` から起動できます。
- 主要な回帰確認は `tests/` の Python テストで追えます。
- 最終確認では Minecraft サーバ接続、ログイン、スポーン、応答生成まで確認できました。

## 実装済みの拡張モジュール

- `mindcraft_py.task_coordinator` に、中央タスク管理機構の `AcquireTask` / `YieldTask` 相当を追加しました。
- タスクは `depends_on` を持ち、先行タスクの完了を前提に取得されます。
- `MindcraftRuntime` からは `register_task` / `list_tasks` / `acquire_task` / `yield_task` を直接扱えます。
- `mindcraft_py.environment` に、空間情報の要約とコンテキストベースのインベントリ抽出を追加しました。
- `mindcraft_py.llm_gateway` に、JSON Schema 付きの生成要求と再試行付きパース処理を追加しました。
- これらは `mindcraft_py` のトップレベルからも再エクスポートされています。

## 実サーバに接続する場合

- `mock_client: True` のままだと Minecraft なしのモック実行になります。
- 現状の Python 側は、コマンド処理・プロフィール読み込み・Ollama 通信・プロセス制御の土台です。
- Minecraft への実接続は、現状は `node main.js --profiles ./agents/Andy.toml` が確実です。
- Python からも CLI 起動はできますが、内部では既存 JS/Mineflayer 経由の接続を使います。
- `src/process/create_agent_process.js` は薄い分岐だけを持ち、実体は `mindcraft_py/node_agent_process.js` 側に寄っています。
- 以後の移行は `src/agent/` の Mineflayer 非依存部分を Python に寄せるのが中心です。

### モック確認例

```python
runtime = MindcraftRuntime()
runtime.init(port=8080, host_public=False, auto_open_ui=False)
runtime.create_agent({
    "host": "localhost",
    "port": 30000,
    "auth": "offline",
    "mock_client": True,
    "blocked_actions": [],
    "profile": profile,
})
```

## Ollama

- 既定モデル: `sweaterdog/andy-4:q8_0`
- 埋め込みモデル: `embeddinggemma:latest`
- 既定URL: `https://ollama-melchior.arc.upiscium.dev`

### `<think>` の扱い

- 応答内の `<think>...</think>` は削除します。
- `<think>` が開いたまま閉じていない場合は未完了とみなし、再生成します。
- 5回続けて未完了なら、安全側に倒して失敗メッセージを返します。

## テスト

```bash
python -m pytest tests/test_python_commands.py tests/test_ollama_adapter.py
```

追加した拡張の確認は次でも行えます。

```bash
python -m pytest tests/test_task_coordinator.py tests/test_environment_helpers.py tests/test_llm_gateway.py
```

内部ロジック寄りの単体確認は次です。

```bash
python -m pytest tests/test_task_coordinator_unit.py tests/test_runtime_task_pool_unit.py
```

タスクプールの最小デモは次です。

```bash
python scripts/task_pool_demo.py
```

依存解消順に task をたどる BFS デモは次です。

```bash
python scripts/task_pool_bfs_demo.py
```

Python の BFS ランナーを直接使う場合は `mindcraft_py.task_runner.run_dependency_bfs` を参照してください。

デモでは `acquire_task()` / `yield_task()` / `complete_task()` を順に試せます。

TOML 形式の task pool file を読み込む場合は `task_pool_file` を profile や settings に指定します。デモは `tasks/task_pool_demo.toml` を読み込みます。

例:

```toml
task_pool_file = "./tasks/task_pool_demo.toml"
```

CLI から渡す場合は次を使えます。

```bash
python -m mindcraft_py --profiles ./agents/Andy.toml --task_pool_file ./tasks/task_pool_demo.toml
```

エージェント起動確認まで含めるなら:

```bash
python -m pytest tests/test_mock_query_bridge.py tests/test_action_bridge_mock.py tests/test_multiagent_inventory_init.py
```

## 補足

- `settings.js` の `profiles` も TOML 前提です。
- `main.js` は TOML を読み込んでエージェントを起動できます。
- `mindcraft_py.runtime.MindcraftRuntime` には、エージェント状態の登録・更新・取得を行う API が追加されています。
- JS の MindServer は可視化/UI と Socket.IO の入口として残し、状態の実体は Python 側へ寄せています。
- `mindcraft_py.mindserver_state.MindserverState` が Python 側の状態レジストリです。
- `src/mindcraft/agent_registry.js` は JS 側の薄いブリッジとして残っています。
- `src/mindcraft/mindserver.js` は表示/UI の入出力を担当し、開始/停止の結果は Python 状態と連動します。
- `src/mindcraft/agent_registry.js` で JS 側の agent 状態を薄く管理しつつ、Python 側の状態 API と合わせて移行しています。
- まずは `agents/Andy.toml` で確認するのが簡単です。

## 検証結果

- `just test`: PASS
- `just check`: PASS
- 実機確認: PASS（MindServer 接続、Minecraft ログイン、スポーン、応答生成まで確認）
