# Mindcraft コア機能まとめ（図解版）

このドキュメントは `docs/core-features.md` の内容を、Mermaid図で俯瞰しやすく再構成した版です。

## 全体アーキテクチャ

```mermaid
flowchart LR
    U[CLI / Env<br/>main.js + settings.js] --> M[Mindcraft Runtime]
    M --> S[MindServer<br/>express + socket.io]
    M --> P[AgentProcess x N<br/>spawn / restart]

    S --> W[Web UI / External Client]
    S --> ST[state-update stream]

    P --> A[Agent Core Loop<br/>history + prompter + action manager]
    A --> MC[Minecraft Server]
    A --> LLM[LLM Providers<br/>OpenAI / Anthropic / ...]
    A --> V[Vision Model]
    A --> T[Task Framework]
    A --> C[Coder Sandbox]
```

対応項目: 1, 2, 3, 4, 5, 11, 13, 14, 15

## 起動・設定・プロセス管理

```mermaid
sequenceDiagram
    participant CLI as CLI(main.js)
    participant CFG as settings/env
    participant CORE as mindcraft.js
    participant PROC as AgentProcess
    participant AG as init_agent.js

    CLI->>CFG: --profiles / --task_path / --task_id + Env
    CLI->>CORE: createAgent(settings)
    CORE->>PROC: spawn node src/process/init_agent.js
    PROC->>AG: boot agent runtime
    PROC-->>CORE: exit code / restart signal
    PROC->>PROC: watchdog + forceRestart()
```

対応項目: 1, 3, 4

## MindServer（制御ハブ + 状態配信）

```mermaid
flowchart TD
    subgraph Hub[MindServer]
      REG[registerAgent]
      AS[agents-status emit]
      LSN[listen-to-agents]
      POLL[1秒ごとに get-full-state]
      STU[state-update emit]
    end

    AC1[Agent Connection 1] --> REG
    AC2[Agent Connection 2] --> REG
    REG --> AS
    LSN --> POLL --> STU
    STU --> WEB[Web UI / Listener]
```

対応項目: 2

## エージェント中核ループ

```mermaid
flowchart TD
    MSG[受信メッセージ] --> HIS[Historyに保存]
    HIS --> PR[Prompterでprompt生成]
    PR --> LLM[LLM応答]
    LLM --> PARSE{!command を含む?}
    PARSE -- Yes --> CMD[executeCommand]
    CMD --> ACT[ActionManagerで実行]
    ACT --> OUT[結果を履歴/発話へ反映]
    PARSE -- No --> CHAT[会話返信]
    CHAT --> OUT
    OUT --> LOOP[300ms update loop]
    LOOP --> MODES[modes/self-prompt/task判定]
    MODES --> MSG
```

対応項目: 5, 7, 8, 10

## コマンドDSL実行パイプライン

```mermaid
flowchart LR
    R[LLM response] --> X[コマンド抽出<br/>!name(args)]
    X --> V[型・domain検証]
    V --> MAP[commandMap lookup<br/>actions + queries]
    MAP --> BL{blacklist対象?}
    BL -- Yes --> REJ[拒否/無効化]
    BL -- No --> RUN[perform実行]
    RUN --> RES[system結果文字列]
```

対応項目: 6

## マルチエージェント会話制御

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active: startConversation
    Active --> Queueing: message received
    Queueing --> FastReply: 両者idle or talk-over可
    Queueing --> DelayedReply: 相手busy
    Queueing --> LLMDecide: 自分busy/相手idle
    LLMDecide --> FastReply: respond
    LLMDecide --> Active: ignore
    FastReply --> Active
    DelayedReply --> Active
    Active --> Idle: endConversation
```

対応項目: 9

## LLM層（抽象化・プロンプト組立）

```mermaid
flowchart TD
    P[Profile templates] --> RS[replaceStrings]
    H[History turns] --> RS
    D[Docs/Examples/Memory] --> RS
    RS --> SYS[System Prompt]
    SYS --> MM[_model_map.js]
    MM --> OA[OpenAI family]
    MM --> AN[Anthropic family]
    MM --> OT[Other providers]
    OA --> RET[LLM text output]
    AN --> RET
    OT --> RET
```

対応項目: 11

## スキル・タスク・評価

```mermaid
flowchart LR
    TASK[Task definition<br/>Crafting/Cooking/Construction] --> INIT[初期化/配布/ワールド準備]
    INIT --> GOAL[ゴール設定]
    GOAL --> EXEC[Agent actions via skills.js]
    EXEC --> VAL[Task validator / blueprint check]
    VAL --> SCORE[Task ended with score]
```

対応項目: 12, 13

## 画像理解とビューア

```mermaid
sequenceDiagram
    participant A as Agent
    participant VI as VisionInterpreter
    participant VM as Vision Model
    participant BV as Browser Viewer

    A->>VI: lookAtPlayer / lookAtPosition
    VI->>VI: スクリーンショット取得
    VI->>VM: 画像 + prompt
    VM-->>A: 解析テキスト
    A-->>BV: 一人称ビュー配信(prismarine-viewer)
```

対応項目: 14

## `!newAction` サンドボックス実行

```mermaid
flowchart TD
    NA[!newAction] --> G[Coder: codeblock抽出]
    G --> L[ESLint検査]
    L --> OK{lint OK?}
    OK -- No --> FB[エラーをLLMへ返して再試行]
    OK -- Yes --> SES[SES Compartment evaluate]
    SES --> API[公開API: skills/world/Vec3/log]
    API --> RUN[実行 + 割り込み対応]
    RUN --> SUM[出力要約を履歴へ]
```

対応項目: 15

## 設計意図（要約）

- 複数エージェント・複数タスク・複数モデルを同一基盤で運用できる構成。
- 自由度（LLM生成行動）と安全性（モード/割り込み/プロセス分離）を両立。
- 実験実行から評価（スコア）までを一連のワークフローとして提供。
