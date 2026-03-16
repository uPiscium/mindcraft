# Pythonコマンド基盤の着手

## 今回着手した範囲

- `mindcraft_py/commands.py` を追加
- Python側に、LLMへ提示するコマンド仕様の最小レジストリを用意
- Python側でコマンド文字列の検出、切り出し、引数パース、コマンド docs 生成を扱える状態にした

## この段階で含めたコマンド

- `!stats`
- `!inventory`
- `!nearbyBlocks`
- `!entities`
- `!stop`
- `!goal`
- `!newAction`

## 位置づけ

- まだ mineflayer 操作本体をPythonへ移したわけではない
- 先に「LLMが参照するコマンド仕様」をPython側へ持ち込み、JavaScript実装との責務分離を始めた段階
- 今後はこのレジストリを基点に、実行経路をJSアダプタ越しへ寄せていく想定

## ねらい

- LLMに見せる command docs と Python側の制御ロジックを同じ場所で管理できるようにする
- JavaScript側の `src/agent/commands/` をすぐには壊さず、段階移行できる足場を作る
- Query系コマンドから順に移植しやすい形にする

## 次の候補

- Pythonレジストリと MindServer 間の実行ブリッジを追加
- Query系コマンドの実処理を Python 呼び出しへ移す
- `src/models/prompter.js` が参照する command docs の供給元を段階的に切り替える
