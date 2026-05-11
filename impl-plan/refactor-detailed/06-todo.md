# Refactor TODO

## 00 Overview
- [ ] 既存の入出力仕様を列挙する
- [ ] 依存方向の基準を図式化する
- [ ] 実装順と移行順を一致させる
- [ ] 各章のテスト担当範囲を明記する

## 01 Bootstrap and Entry
- [ ] CLI parser を抽出する
- [ ] env と CLI のマージ関数を抽出する
- [ ] 起動前バリデーションを独立させる
- [ ] bootstrap context 型を定義する
- [ ] `main` を compose/execute のみにする
- [ ] 必須設定不足時のエラー形式を決める
- [ ] 設定解決の単体テストを追加する

## 02 Config and Model Abstraction
- [ ] settings schema を定義する
- [ ] profile schema を定義する
- [ ] task schema を定義する
- [ ] model descriptor 正規化関数を作る
- [ ] provider interface を統一する
- [ ] 未対応 provider の失敗経路を作る
- [ ] profile と global の優先順位を固定する
- [ ] 設定/モデルのユニットテストを追加する

## 03 Agent Runtime
- [ ] Agent の責務を orchestration に限定する
- [ ] conversation service を分離する
- [ ] command dispatcher を分離する
- [ ] history / memory / prompt builder を切り出す
- [ ] response router を source 別に分ける
- [ ] 状態構造体を定義する
- [ ] 1ターン処理と継続処理を分ける
- [ ] 失敗時の状態保全テストを追加する

## 04 Server and Process Control
- [ ] server state store を分離する
- [ ] process launcher を分離する
- [ ] signal sender wrapper を作る
- [ ] socket event router を切り出す
- [ ] restart policy を設定化する
- [ ] start/stop/restart の状態機械を定義する
- [ ] 起動/停止/再起動のテストを追加する

## 05 Tasks and Extensions
- [ ] task schema を定義する
- [ ] completion evaluator を純粋関数化する
- [ ] vision pipeline を preprocess/extract に分ける
- [ ] memory gateway を read/write に分ける
- [ ] skill selection policy を作る
- [ ] extension registry を core から切り離す
- [ ] extension 有効/無効の切替を実装する
- [ ] 拡張分離のテストを追加する

## Final Checks
- [ ] 既存挙動が維持されていることを確認する
- [ ] 各章のユニットテストが独立に回ることを確認する
- [ ] 外部 I/O がモック前提になっていることを確認する
- [ ] 依存方向が逆転していないことを確認する
