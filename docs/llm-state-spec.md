# LLMに渡されるエージェントState仕様（実装抽出）

この文書は、現行実装から「エージェントの現在状態」がLLMへどの形式で渡されるかを、コード上の事実ベースで整理したものです。

## 結論（重要）

- **LLMに直接渡される現在状態は、JSONではなくテキスト置換（プレースホルダ展開）です。**
- `src/agent/library/full_state.js` の `getFullState()` が返すJSONは、**MindServerの状態配信 (`state-update`) 用**であり、現行コードではLLMプロンプトには注入されません。

---

## 1) LLMへ渡るStateの実体（テキスト）

状態テキストは `Prompter.replaceStrings()` でプロファイル文面中のプレースホルダを置換して生成されます。

- 実装: `src/models/prompter.js:136`
- 主な呼び出し:
  - 会話: `promptConvo()` → `replaceStrings()` (`src/models/prompter.js:213`)
  - コード生成: `promptCoding()` → `replaceStrings()` (`src/models/prompter.js:263`)
  - 視覚解析: `promptVision()` → `replaceStrings()` (`src/models/prompter.js:302`)
  - memory保存: `promptMemSaving()` → `replaceStrings()` (`src/models/prompter.js:279`)
  - bot応答判定: `promptShouldRespondToBot()` → `replaceStrings()` (`src/models/prompter.js:292`)

### 1.1 `$STATS` の厳密フォーマット

`$STATS` は `!stats` コマンド出力 + `!entities` 出力 + `!nearbyBlocks` 出力を連結して生成。

- 実装: `src/models/prompter.js:139`
- `!stats` 実装: `src/agent/commands/queries.js:15`

`!stats` の出力テンプレート（実装準拠、改行/文言そのまま）:

```text
\nSTATS
- Position: x: <x.toFixed(2)>, y: <y.toFixed(2)>, z: <z.toFixed(2)>
- Gamemode: <bot.game.gameMode>
- Health: <round(bot.health)> / 20
- Hunger: <round(bot.food)> / 20
- Biome: <world.getBiomeName(bot)>
- Weather: <Clear|Rain|Thunderstorm>
- Time: <Morning|Afternoon|Night>
- Current Action: <Idle or agent.actions.currentActionLabel>
- Nearby Human Players: <comma list | None.>
- Nearby Bot Players: <comma list | None.>
<agent.bot.modes.getMiniDocs()>
\n
```

補足:
- `Weather` は `rainState>0` で Rain, `thunderState>0` で Thunderstorm（後者が上書き）。
- `Time` は `timeOfDay < 6000 => Morning`, `<12000 => Afternoon`, それ以外 Night。

### 1.2 `$INVENTORY` の厳密フォーマット

- 実装: `src/models/prompter.js:145`
- `!inventory` 実装: `src/agent/commands/queries.js:67`

`!inventory` の出力テンプレート（実装準拠）:

```text
\nINVENTORY
- <item_name>: <count>
... (0個より大きい項目のみ)

# アイテムが1つもない場合
\nINVENTORY: Nothing

# クリエイティブモードの場合（在庫あり分の列挙後）
(You have infinite items in creative mode. You do not need to gather resources!!)

WEARING: 
Head: <helmet name>
Torso: <chestplate name>
Legs: <leggings name>
Feet: <boots name>

# 装備なし
WEARING: Nothing
\n
```

### 1.3 その他、Stateに関わるプレースホルダ

`replaceStrings()` で処理される状態系プレースホルダ:

- `$ACTION`: `agent.actions.currentActionLabel`（そのまま）
  - 実装: `src/models/prompter.js:149`
- `$SELF_PROMPT`: 自己目標が停止中でないときのみ
  - `YOUR CURRENT ASSIGNED GOAL: "<prompt>"\n`
  - 実装: `src/models/prompter.js:172`
- `$MEMORY`: `agent.history.memory`
  - 実装: `src/models/prompter.js:166`
- `$TO_SUMMARIZE`: `stringifyTurns(to_summarize)`
  - 実装: `src/models/prompter.js:168`
- `$CONVO`: `Recent conversation:\n` + `stringifyTurns(messages)`
  - 実装: `src/models/prompter.js:170`
- `$LAST_GOALS`: 直近目標の成功/失敗文を列挙
  - 実装: `src/models/prompter.js:177`

これらは主に `profiles/defaults/_default.json` の `conversing`, `coding`, `saving_memory`, `bot_responder`, `image_analysis` に埋め込まれ、LLMのsystem promptへ入ります。

- 参照: `profiles/defaults/_default.json:4`

---

## 2) JSON State（`getFullState`）の仕様

`getFullState(agent)` は以下のJSONを構築します。

- 実装: `src/agent/library/full_state.js:12`
- 利用箇所:
  - Agent側で `get-full-state` イベント受信時に返却: `src/agent/mindserver_proxy.js:72`
  - MindServerが1秒ごとに収集し `state-update` で配信: `src/mindcraft/mindserver.js:250`

### 2.1 オブジェクト形（実装準拠）

```json
{
  "name": "<agent.name>",
  "gameplay": {
    "position": { "x": 0.0, "y": 0.0, "z": 0.0 },
    "dimension": "<bot.game.dimension>",
    "gamemode": "<bot.game.gameMode>",
    "health": 20,
    "hunger": 20,
    "biome": "<getBiomeName(bot)>",
    "weather": "Clear|Rain|Thunderstorm",
    "timeOfDay": 0,
    "timeLabel": "Morning|Afternoon|Night"
  },
  "action": {
    "current": "Idle|<currentActionLabel>",
    "isIdle": true
  },
  "surroundings": {
    "below": "<block name>",
    "legs": "<block name>",
    "head": "<block name>",
    "firstBlockAboveHead": "<block name or null-ish>"
  },
  "inventory": {
    "counts": {
      "<item_name>": 12
    },
    "stacksUsed": 5,
    "totalSlots": 46,
    "equipment": {
      "helmet": null,
      "chestplate": null,
      "leggings": null,
      "boots": null,
      "mainHand": null
    }
  },
  "nearby": {
    "humanPlayers": ["player1"],
    "botPlayers": ["agentB"],
    "entityTypes": ["zombie", "cow"]
  },
  "modes": {
    "summary": "<bot.modes.getMiniDocs()>"
  }
}
```

注記:
- `position` は小数第2位に丸め (`toFixed(2)` → Number)。
- `nearby.entityTypes` は `player` と `item` を除外。

---

## 3) JSON Schema（厳密化）

機械可読のスキーマは `docs/schemas/full-state.schema.json` に定義。

（本スキーマは `getFullState()` の現行実装に合わせた抽出版であり、値域の一部は実行環境依存のため緩めに許容しています。）

---

## 4) LLM入力としての最終形

モデル呼び出し時の構造は概ね以下です。

- system message: プロファイル文面 + 上記プレースホルダ置換済みテキスト
- turns/messages: 履歴メッセージ配列

例:
- OpenAI系: `instructions` にsystem、`input` にturns（`src/models/gpt.js:63`）
- Anthropic系: `system` にsystem、`messages` にturns（`src/models/claude.js:33`）

つまり、**StateはLLMに対して「プロンプト内テキストとして供給」される**のが現在の正確な仕様です。
