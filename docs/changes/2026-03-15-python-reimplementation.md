# Python再実装（mineflayerはJavaScriptブリッジ利用）

## 目的

本リポジトリの実行フローをPython主体で扱えるように再構成しつつ、mineflayer依存部分はJavaScript側に残して利用する構成へ移行しました。

## 実装方針

- **Mineflayer/エージェント実行基盤はJavaScriptを継続利用**
  - Minecraft接続、bot生成、agent process管理、MindServerは既存JavaScript実装をそのまま活用。
- **アプリの起動・設定解決・API利用入口をPython側に移行**
  - PythonランタイムからNodeプロセスを起動し、Socket.IO経由でMindServer APIを利用する方式に統一。
- **JavaScriptの再利用が有利な処理はブリッジ化**
  - 既存の`settings.js`とCLI/envオーバーライド仕様を保つため、設定解決はNodeスクリプトをPythonから呼び出す形を採用。

## 主な変更内容

### 1) Python実行エントリの追加

- `main.py` をPython版の実行エントリとして追加。
- CLI引数を受け取り、Python側ランナー経由でMindcraft起動・エージェント作成・待機までを実行。

### 2) Pythonパッケージ層の新設

`mindcraft_py/` を新設し、以下の責務に分離。

- `runtime.py`
  - Node側初期化スクリプトをサブプロセス起動
  - MindServer起動待機
  - Socket.IO接続
  - `create-agent` API呼び出し
  - シャットダウン/待機処理
- `config.py`
  - 設定解決をJavaScriptブリッジで実施し、PythonにJSONとして取り込み
- `runner.py`
  - `main.js`相当のフロー（設定取得→profile読込→agent生成→待機）をPythonで実装
- `__init__.py`, `__main__.py`
  - ライブラリ利用と`python -m mindcraft_py`実行の両方をサポート

### 3) JavaScriptブリッジの整備

- `src/mindcraft-py/init-mindcraft.js`
  - PythonからMindServer起動時に必要な`host_public`/`auto_open_ui`引数を受け取れるよう拡張。
- `src/mindcraft-py/resolve-settings.js`（新規）
  - 既存`main.js`の設定解決ロジック（CLI引数 + 環境変数オーバーライド）を切り出し。
  - Pythonはこのスクリプトを呼び出して、既存仕様互換の設定を取得。

### 4) 既存Pythonブリッジの再配置・互換導線

- `src/mindcraft-py/mindcraft.py` を薄い互換レイヤとして整理し、新しい`mindcraft_py`パッケージを参照する形に変更。
- `src/mindcraft-py/example.py` も新パッケージ利用に更新。

## 期待される効果

- 実行オーケストレーションをPythonへ寄せつつ、mineflayer由来のJavaScript資産を安全に再利用可能。
- `settings.js`中心の既存設定資産とCLI/env仕様を維持し、移行コストを抑制。
- Pythonからの組み込み利用（API的利用）とCLI利用の両方に対応。

## 利用方法（新フロー）

- Pythonエントリ実行: `python main.py [--profiles ... --task_path ... --task_id ...]`
- モジュール実行: `python -m mindcraft_py [--profiles ... --task_path ... --task_id ...]`
- ライブラリ利用:
  - `mindcraft_py.init()`
  - `mindcraft_py.create_agent({...})`
  - `mindcraft_py.wait()` / `mindcraft_py.shutdown()`

## 補足

- mineflayer本体・Minecraft接続制御はJavaScript継続です。
- 設定解決はJavaScriptブリッジ経由のため、Node依存は引き続き必要です。

## 追記（依存管理のuv移行）

- Python依存管理を`requirements.txt`から`uv`ベースへ移行。
- `pyproject.toml`にPython依存を集約し、`uv lock`で`uv.lock`を生成。
- セットアップ・実行手順を`README_PYTHON.md`で`uv sync`/`uv run`前提に更新。
