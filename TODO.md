# TODO

現状の残タスクを、優先順位順に整理したものです。

## Priority 1: 設定/プロファイルの運用固定

### 1. `settings.toml` と profile TOML の運用ルールを確定する

- `settings.toml` と `agents/*.toml` はすでに動作する
- JSON/TOML を併用するか、今後どちらかに寄せるか決める
- `README_PYTHON.md` と実運用設定の差分を減らす
- `just catalog` で command catalog を再生成する運用を継続する

### 2. `command_catalog` 生成手順をCI/運用に組み込む

- Python registry から生成する方針は固まった
- 生成タイミング（手動 / 起動時 / CI）をどこに置くか決める
- `mindcraft_py/command_catalog.json` の更新漏れを防ぐ

## Priority 2: テスト/モックの拡張

### 3. mock client の応答をさらに増やす

- `!inventory`, `!nearbyBlocks`, `!entities`, `!craftable`, `!help`, `!goal`, `!stop`, `!newAction` は最低限動く
- `techtree` / `construction` のタスクに合わせた応答を追加する
- 失敗系の応答や状態差分も扱えるようにする

### 4. 実 Minecraft 環境での multi-agent 回帰確認を増やす

- `multiagent_techtree_1_shears` は一度通ったので、他タスクも確認する
- `multiagent_techtree_1_wooden_pickaxe` など、初期インベントリ差分があるタスクを試す
- タスクごとの失敗パターンを記録する

## Priority 3: 依存関係の健全化

### 5. `npm audit` の high 警告を整理する

- `patch-package` 警告は解消済み
- ただし依存ツリーに high 脆弱性が残っているため、影響範囲を確認する
- すぐ直せないものは、どれを許容するか記録する

## Priority 4: ドキュメント/開発フロー

### 6. PR/マージ履歴に合わせて文書を整える

- `README_PYTHON.md` の説明は概ね現状に追従している
- 必要なら `README.md` 側にも Python runtime の導線を追記する
- `AGENTS.md` はインデックスに保ち、運用情報は `agent-docs/` に集約する

### 7. ブランチ/マージ運用のルールを簡潔に残す

- `feature/python-command-infra` はすでにマージ済み
- `fix/multiagent-inventory-init` もマージ済み
- `feature/todo-followup` は今回の作業ブランチとして扱う
- 次の作業でも変更ごとに短いブランチを切る運用を続ける

## Notes

- 現在の `develop` では、Python command registry / bridge / mock client / TOML profile は動作する
- 直近の focus は「運用ルールの固定」と「mock/action テストの補強」
