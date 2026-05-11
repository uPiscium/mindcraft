# Refactor Plan Overview

## Goal
Mindcraft を「設定」「管理サーバ」「エージェント実行」「LLM」「タスク」の境界で再分割し、ユニットテスト可能な構造にする。

## Split Policy
- 1ファイル1責務に寄せる
- 外部I/Oを薄い層へ隔離する
- 仕様は先にテストへ落とす
- 既存挙動は壊さず、内部構造だけを段階的に置き換える

## Package Map
- `01-bootstrap.md`: 起動と設定の最小土台
- `02-config-and-models.md`: 設定・プロファイル・LLM抽象化
- `03-agent-runtime.md`: Agent 本体と対話/コマンド処理
- `04-server-and-process.md`: 管理サーバと子プロセス制御
- `05-tasks-and-extension.md`: タスク・視覚・記憶・NPC 拡張

## Execution Order
1. Bootstrap を切り出して起動経路を安定化する
2. Config と model を固定して依存境界を作る
3. Agent runtime を純化して会話処理を分離する
4. Server/process を整理して外部実行を隔離する
5. Tasks/extension を後付け可能な拡張点に切る

## Global Requirements
- 既存の入出力仕様は維持する
- 新しい公開 API は最小限にする
- 依存方向は `ui -> server -> runtime -> model -> config` を基本にする
- 外部依存はインターフェース越しに差し替え可能にする

## Shared Test Rules
- 各章に機能要件を列挙する
- 各要件に対応するユニットテストを列挙する
- 外部 I/O はモックで置き換える
- 実装前に失敗するテストを先に書ける状態にする
