# Python 利用手順

このリポジトリでは、Minecraft 接続とエージェント制御の一部を Python から利用できます。

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

Python 側でプロセスを制御したい場合は `mindcraft_py.runtime.MindcraftRuntime` の
`start_agent_process()` / `stop_agent()` / `restart_agent()` を使います。

## 実サーバに接続する場合

- `mock_client: True` のままだと Minecraft なしのモック実行になります。
- 現状の Python 側は、コマンド処理・プロフィール読み込み・Ollama 通信の土台です。
- Minecraft への実接続を行う起動は、いまは `node main.js --profiles ./agents/Andy.toml` が確実です。
- Python からは、まずモックで挙動確認し、実接続は既存 JS 起動を使うのが安全です。

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

エージェント起動確認まで含めるなら:

```bash
python -m pytest tests/test_mock_query_bridge.py tests/test_action_bridge_mock.py tests/test_multiagent_inventory_init.py
```

## 補足

- `settings.js` の `profiles` も TOML 前提です。
- `main.js` は TOML を読み込んでエージェントを起動できます。
- まずは `agents/Andy.toml` で確認するのが簡単です。
