# 04 Server and Process Control

## Scope
- MindServer 相当の管理サーバ
- AgentProcess 相当の子プロセス制御
- agent 登録、停止、再起動

## Functional Requirements
- FR-1: 管理サーバは agent の状態一覧を提供できる
- FR-2: agent 登録/解除が状態に反映される
- FR-3: 子プロセス起動引数が一元管理される
- FR-4: 子プロセス異常終了時の扱いが明確である
- FR-5: UI/外部クライアントは socket 互換のイベントで操作できる

## Unit Tests
- UT-1: agent 登録時にメタデータが保存される
- UT-2: agent 解除時に一覧から消える
- UT-3: 起動コマンド生成が期待どおりになる
- UT-4: stop/restart のシグナル送信が正しい
- UT-5: 異常終了時の再起動判定が期待どおりになる
- UT-6: サーバイベントが適切なハンドラへルーティングされる

## Done Criteria
- 親プロセスと子プロセスの責務が分離される
- 起動/停止の状態遷移をテストで守れる
