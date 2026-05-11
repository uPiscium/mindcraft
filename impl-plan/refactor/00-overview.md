# Refactor Plan Overview

## Goal
Mindcraft を「設定」「管理サーバ」「エージェント実行」「LLM」「タスク」の境界で再分割し、ユニットテスト可能な構造にする。

## Split Policy
- 1ファイル1責務に寄せる
- 外部I/Oを薄い層へ隔離する
- 仕様は先にテストへ落とす
- 既存挙動は壊さず、内部構造だけを段階的に置き換える

## Work Packages
1. `01-bootstrap.md`: 起動と設定の最小土台
2. `02-config-and-models.md`: 設定・プロファイル・LLM抽象化
3. `03-agent-runtime.md`: Agent 本体と対話/コマンド処理
4. `04-server-and-process.md`: 管理サーバと子プロセス制御
5. `05-tasks-and-extension.md`: タスク・視覚・記憶・NPC 拡張

## Test Rule
各ワークパッケージは以下を満たすこと。
- 機能要件が明文化されている
- その要件を検証するユニットテストが列挙されている
- 外部依存はモック化前提になっている
