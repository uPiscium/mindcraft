# TODO

Pythonコマンド移行まわりの残タスクを、優先順位つきで整理したものです。

## Priority 1: 実行経路の拡張

### 1. action 系 bridge の追加

- Python registry から JavaScript 実行アダプタへ action コマンドを渡せるようにする
- 対象候補: `!stop`, `!goal`, その後に他の action 群
- query 系と同様に、MindServer 経由で呼べる共通インターフェースに寄せる
- Python 側から action/query の責務が見分けられる状態を維持する

### 2. query 系コマンドの移行範囲を広げる

- 現在 Python 側に持っているコマンドは `!stats`, `!inventory`, `!nearbyBlocks`, `!entities`, `!craftable`, `!modes`, `!savedPlaces`, `!checkBlueprintLevel`, `!checkBlueprint`, `!getBlueprint`, `!getBlueprintLevel`, `!getCraftingPlan`, `!searchWiki`, `!help`, `!stop`, `!goal`, `!newAction`
- Python registry と JS 側 `src/agent/commands/*.js` の対応範囲を広げる

## Priority 2: テスト基盤の強化

### 3. mock client の応答を拡張する

- 現在の mock client は query bridge 疎通確認向けの最小実装
- `!inventory`, `!nearbyBlocks`, `!entities`, `!craftable`, `!help` などの返答バリエーションを増やす
- 失敗系の応答や、より現実に近い状態データも返せるようにする

### 4. action 系の mock テストを追加する

- action bridge 実装後、Minecraft 非起動でテストできるよう mock client を拡張する
- 成功・失敗・タイムアウトのテストケースを用意する
- Python から JS アダプタへの往復動作をテストで固定する

### 5. 実 Minecraft 環境での統合確認を増やす

- mock client は Mineflayer の実挙動までは再現しない
- 実ワールド接続で query / action bridge が期待通り動くか確認する
- 代表タスクを使った回帰確認手順を整理する

## Priority 3: Python 側への責務移行

### 6. command docs の供給元切り替えを検討する

- いまは Python 側で command registry を持ちつつ、JS 側にも docs 生成経路が残っている
- `src/models/prompter.js` が参照する command docs の供給元を段階的に切り替えるか検討する
- LLM に見せる仕様と Python 側 registry の一元管理を目指す

### 7. Python registry の自動生成・同期戦略を決める

- 現在は JS 側仕様を抽出して Python 側と比較している
- 将来的に Python 側を正とするのか、JS 側を正とするのかを明確にする
- 二重管理コストを減らす方法を決める

## Priority 4: 開発フロー整備

### 8. PR / push の準備

- 現在の `feature/python-command-infra` ブランチを push して共有できる状態にする
- 必要なら変更内容をまとめて PR 本文用の要約を作る

### 9. ドキュメントの更新範囲を広げる

- `README_PYTHON.md` は更新済み
- 必要なら `README.md` に Python runtime や `just` / `pytest` / `ruff` の導線を追加する
- mock client の位置づけと制約も明記する

## Notes

- 現時点では mock client により、Minecraft 非起動でも Python query bridge のテストは可能
- ただし mineflayer 実体の移動、採掘、インベントリ同期などは実 Minecraft 環境で別途確認が必要
