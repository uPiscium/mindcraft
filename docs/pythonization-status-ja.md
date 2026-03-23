# 現状Python化されていない部分と、その理由

## 結論（全体像）

現在のmindcraftは、**実行オーケストレーションはPython**、**Minecraft実働部分はJavaScript**というハイブリッド構成です。  
そのため、Python化されていない領域は「未着手」ではなく、設計上の意図に基づいて残されています。

- Python化済み: 起動入口・設定解決・実行制御
  - `main.py`
  - `mindcraft_py/runner.py`
  - `mindcraft_py/runtime.py`
  - `mindcraft_py/config.py`
- 非Python化（意図的にJS継続）: Minecraft接続・Bot行動・MindServer・モデル実装の中核
  - `src/**/*.js`

この方針は変更履歴にも明記されており、**mineflayer依存部分はJavaScript側を継続利用**する前提です。

- `docs/changes/2026-03-15-python-reimplementation.md`

## Python化されていない主な領域

### 1. Mineflayer依存の実ゲーム操作層

対象例:

- `src/agent/agent.js`
- `src/agent/commands/actions.js`
- `src/utils/mcdata.js`

理由:

- ボット操作の中核が`mineflayer`系ライブラリに強く依存しているため。
- 実装がMineflayerイベントモデル（spawn/login/chat/行動制御など）に深く結合しており、Pythonへ移植すると大規模な書き換えが必要。
- 既存の挙動安定性（行動、復帰、コマンド実行）を壊さず段階移行するには、当面JS維持が合理的。

関連依存:

- `package.json` の `mineflayer`, `mineflayer-pathfinder`, `mineflayer-pvp`, `minecraft-data` など

### 2. Minecraftサーバ検出・接続判定

対象例:

- `src/mindcraft/mcserver.js`

理由:

- `minecraft-protocol`等のNodeライブラリ前提で実装されているため。
- LANスキャン、バージョン解決、接続前検証などを同等品質でPython再実装するコストが高い。
- 既存の接続ロジックを再利用するほうが互換性リスクが低い。

### 3. MindServer（Socket.IO API + Web UIホスト）

対象例:

- `src/mindcraft/mindserver.js`
- `src/mindcraft/mindcraft.js`

理由:

- エージェント管理API、状態配信、UI静的配信がJSで統合されているため。
- Socket.IOイベント（`create-agent`, `agents-status`, `state-update`など）を含む既存クライアントとの互換を保つため。
- Python側はこのMindServerを呼び出すクライアントとして接続する設計で、責務分離が明確。

### 4. エージェント子プロセス管理

対象例:

- `src/process/agent_process.js`
- `src/process/init_agent.js`

理由:

- 現行設計がNodeプロセスのspawn・監視・再起動制御を前提としているため。
- プロセス異常時の再起動ポリシーや既存ログフローがJS側に集約済み。
- Python側は上位オーケストレーションに留め、実行プロセスは既存JS資産を活用する方が移行リスクが低い。

### 5. モデルプロバイダ統合レイヤ

対象例:

- `src/models/_model_map.js`
- `src/models/*.js`

理由:

- OpenAI/Anthropic/Google/Groq等の複数プロバイダ統合がJSで実装済み。
- 動的ロードや既存profile仕様との互換を維持するため、短期では移植優先度が低い。
- まず実行入口をPython化し、下位の実行コアは再利用する段階移行方針。

## なぜこの構成なのか（設計意図）

### 段階移行でリスク最小化

- Pythonから操作可能にしつつ、実績のあるJSコアをそのまま利用。
- 全面移植による回 regressions（行動不安定化、接続不整合）を回避。

### 移行コストの最適化

- 高コスト領域（Mineflayer接続・実行ループ）を後回しにし、効果の高い入口側（CLI/API）からPython化。
- 開発速度と安定性のバランスを確保。

### 既存運用との互換性維持

- `settings.js`、既存profiles、既存タスク運用を壊さず導入可能。
- Python導入後もNode資産を使い続けられるため、ユーザーの移行負担が小さい。

## 現在の依存関係の実態

- PythonランタイムはNodeプロセスを起動してMindServerへ接続する。
  - `mindcraft_py/runtime.py`
  - `src/mindcraft-py/init-mindcraft.js`
- そのため、**Python版でもNode.js依存は必須**。
  - `README_PYTHON.md`

## 進捗としてPython化が進んでいる領域

- 設定解決はJSブリッジ依存からPython側完結へ整理済み。
  - `mindcraft_py/config.py`
- タスク実行の呼び出し経路もPythonエントリへ統一が進んでいる。
  - `docs/changes/2026-03-15-python-js-dependency-scope.md`

## まとめ

Python化されていない部分は主に、**Mineflayerを中心とするMinecraft実行コア**と、そこに密結合した**MindServer/プロセス管理/モデル統合層**です。  
これらは技術的難易度と互換性リスクが高いため、現状は「Pythonから制御し、JSコアを再利用する」構成が採用されています。  
つまり、現状の非Python化領域は未対応ではなく、**段階移行戦略として意図的に維持されている領域**です。
