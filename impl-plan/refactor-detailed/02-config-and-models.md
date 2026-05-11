# 02 Config and Model Abstraction

## Scope
- `settings` / `profile` / `task` のスキーマ化
- LLM provider 抽象化
- モデル選択ロジック
- 設定正規化
- provider 能力差の吸収

## Functional Requirements
- FR-1: 設定はスキーマで検証される
- FR-2: profile は名前、モデル、プロンプト、例文を保持できる
- FR-3: model 指定は文字列形式とオブジェクト形式の両方を扱える
- FR-4: provider ごとの差異は共通 IF で吸収される
- FR-5: 未対応 provider は検出可能である
- FR-6: 既定値補完後の設定は実行側がそのまま使える
- FR-7: モデル選択は profile 優先と global 既定を区別できる

## Implementation Breakdown
- schema 層で validation を完結させる
- profile 解決を settings 解決から分離する
- model descriptor を正規化関数で統一する
- provider adapter を interface で揃える
- capability チェックを実行前に行う

## Unit Tests
- UT-1: 有効な設定だけが通る
- UT-2: 無効な設定は検証エラーになる
- UT-3: 文字列モデル指定が正しい provider/model に分解される
- UT-4: オブジェクト形式モデル指定が正しく正規化される
- UT-5: 未対応 provider が適切に失敗する
- UT-6: 共通 `chat()` IF が各 provider 実装で揃う
- UT-7: profile の既定値補完が期待どおりになる
- UT-8: global と profile の優先順位が守られる

## Done Criteria
- モデル関連の条件分岐が散らばらない
- provider 追加が単一責務で済む
- 設定から実行までの変換経路が明確になる
