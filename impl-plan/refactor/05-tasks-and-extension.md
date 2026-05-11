# 05 Tasks and Extensions

## Scope
- task 定義と完了判定
- vision, npc, memory, skill library
- 将来の機能追加ポイント

## Functional Requirements
- FR-1: task は宣言的 JSON から構築できる
- FR-2: task の完了条件を純粋関数として判定できる
- FR-3: vision interpreter は入力画像から必要情報を抽出できる
- FR-4: memory bank は読み書きの境界を持つ
- FR-5: NPC/skill 機能はコア Agent から分離される

## Unit Tests
- UT-1: task JSON がスキーマ検証を通る
- UT-2: task 完了判定が条件ごとに正しく分岐する
- UT-3: vision 入力の前処理が期待どおりになる
- UT-4: memory の保存/読込が独立して検証できる
- UT-5: skill 選択が設定や状態に応じて変わる
- UT-6: 拡張モジュールが core を直接汚染しない

## Done Criteria
- 拡張機能を追加しても core のテストが壊れにくい
- task と補助機能が後付け可能な構造になる
