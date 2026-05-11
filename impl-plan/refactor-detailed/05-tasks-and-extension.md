# 05 Tasks and Extensions

## Scope
- task 定義と完了判定
- vision, npc, memory, skill library
- 将来の機能追加ポイント
- 拡張の有効/無効制御

## Functional Requirements
- FR-1: task は宣言的 JSON から構築できる
- FR-2: task の完了条件を純粋関数として判定できる
- FR-3: vision interpreter は入力画像から必要情報を抽出できる
- FR-4: memory bank は読み書きの境界を持つ
- FR-5: NPC/skill 機能はコア Agent から分離される
- FR-6: 拡張モジュールは設定で有効/無効を切り替えられる
- FR-7: 補助機能の追加で core の契約が変わらない

## Implementation Breakdown
- task schema と completion evaluator を分ける
- vision pipeline を preprocess/extract に分解する
- memory gateway を read/write に分ける
- skill selection を policy 化する
- extension registry を core から切り離す

## Unit Tests
- UT-1: task JSON がスキーマ検証を通る
- UT-2: task 完了判定が条件ごとに正しく分岐する
- UT-3: vision 入力の前処理が期待どおりになる
- UT-4: memory の保存/読込が独立して検証できる
- UT-5: skill 選択が設定や状態に応じて変わる
- UT-6: 拡張モジュールが core を直接汚染しない
- UT-7: extension 無効時に処理がスキップされる

## Done Criteria
- 拡張機能を追加しても core のテストが壊れにくい
- task と補助機能が後付け可能な構造になる
- 境界が明確で保守しやすい
