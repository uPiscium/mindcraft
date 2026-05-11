# 03 Agent Runtime

## Scope
- `Agent` 本体
- 会話、コマンド、アクション実行
- 履歴、メモリ、プロンプト生成

## Functional Requirements
- FR-1: Agent は初期化時に依存を注入できる
- FR-2: メッセージ受信時に履歴へ記録される
- FR-3: コマンドと通常会話が分岐される
- FR-4: コマンド実行は ActionManager を経由する
- FR-5: 応答送信は bot と server の両方に対応できる
- FR-6: 履歴・記憶・セルフプロンプトは独立してテスト可能である

## Unit Tests
- UT-1: Agent 初期化時に必要コンポーネントが構築される
- UT-2: 受信メッセージが履歴へ追加される
- UT-3: コマンド入力時に command 実行経路へ入る
- UT-4: 通常メッセージ時にプロンプト生成経路へ入る
- UT-5: ActionManager 呼び出しが期待引数で行われる
- UT-6: 応答ルーティングが source ごとに分岐する

## Done Criteria
- `Agent` の責務がゲーム状態オーケストレーションに収束する
- 会話ロジックがモックで検証できる
