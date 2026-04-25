# Python Runtime Boundary - task 実装の Python 集約方針

## 目的

task pool の中心ロジックを Python 側に寄せ、JS 側は Mineflayer 実行・入出力・コマンド実行の境界に限定する．
これにより、task 定義・依存判定・状態遷移・選択ロジックを一箇所に集約し、実行フローの複雑さを下げる．

## 目標スコープ

### Python に寄せるもの

- task 定義の読み込み
- task pool の状態管理
- `acquire / complete / yield` の状態遷移
- `depends_on` の依存判定
- current task の管理
- task file の検証

### JS に残すもの

- Mineflayer の実行ループ
- `self_prompter` と prompt 生成
- `action_manager` による実アクション実行
- Minecraft への移動・採掘・クラフトなどの world interaction
- UI / chat / log への出力

### 境界の要点

- Python は task の管理・選択・状態遷移の正本
- JS は Mineflayer 実行と self-prompt を担う実行境界
- Python は current task を指示できるが、実際に動かすのは JS

## 役割分担

### Python 側

- task を「何をやるべきか」として解釈する
- 依存と状態から次の task を決める
- task の完了/返却の状態を保持する

### JS 側

- task を「いつ実行するか」に従って実際に動く
- prompt に task を反映する
- 実行結果を Python 側へ通知する

## 接続方式

- JS は task の開始・成功・失敗・中断を Python に通知する
- Python は task pool の状態遷移のみを管理する
- task の選択結果は JS 側に current task として反映する

## 段階的移行案

### Phase 1

- task file loader を Python に寄せる
- current task 管理を Python の runtime に統一する

### Phase 2

- JS 側の task pool 状態管理を薄くする
- JS は Python から受け取った current task を表示・利用するだけにする

### Phase 3

- task selection / dependency resolution の責務を完全に Python に固定する
- JS は実行フローの境界だけを維持する

## 非対象

- Mineflayer の全面移植
- 既存の action / command システムの書き換え
- task 定義フォーマットの再設計

## 関連

- `mindcraft_py/task_coordinator.py`
- `mindcraft_py/runtime.py`
- `src/agent/tasks/task_pool.js`
- `src/agent/agent.js`
- `src/agent/action_manager.js`
- `src/agent/self_prompter.js`
