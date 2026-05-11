# 01 Bootstrap and Entry

## Scope
- `main.js` 相当の起動処理
- CLI 引数と環境変数の統合
- 設定ロードの入口
- 起動前バリデーション
- 実行コンテキスト生成

## Functional Requirements
- FR-1: CLI 引数から `profiles`, `task_path`, `task_id`, `ports` を解決できる
- FR-2: 環境変数が CLI より優先される箇所を定義できる
- FR-3: 起動時に必須設定が不足していれば明示的に失敗する
- FR-4: 起動処理は副作用を持つ処理と純粋な設定解決を分離する
- FR-5: 起動コンテキストは後続処理へ引き渡せる単一オブジェクトにまとまる
- FR-6: エラーは人間が追える形で返す

## Implementation Breakdown
- CLI parser を単独関数に切る
- env merge を単独関数に切る
- validate を単独関数に切る
- bootstrap context をデータ構造として定義する
- `main` は compose と execute だけにする

## Unit Tests
- UT-1: CLI の最小入力で設定オブジェクトが正しく生成される
- UT-2: 環境変数が期待どおり設定を上書きする
- UT-3: 必須設定欠落時に検証エラーになる
- UT-4: 設定解決関数が I/O なしでテストできる
- UT-5: context 生成が純粋関数として動く
- UT-6: 失敗時メッセージに不足項目が含まれる

## Done Criteria
- エントリ処理が薄くなる
- 設定解決ロジックが単体テスト可能になる
- 起動時の失敗原因が追跡しやすい
