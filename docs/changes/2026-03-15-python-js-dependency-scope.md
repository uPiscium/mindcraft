# Python側のJavaScript依存範囲整理

## 対象

- Python実行経路のうち、mineflayerそのものを直接扱わない箇所

## 変更箇所

- `mindcraft_py/config.py`
  - Python側で設定解決を完結させる経路へ整理
- `tasks/run_task_file.py`
  - タスク実行の呼び出し先をPythonエントリへ統一
- `tasks/human_ai_tasks.py`
  - タスク実行の呼び出し先をPythonエントリへ統一
- `tasks/evaluation_script.py`
  - 実験実行時のメイン起動経路をPythonエントリへ統一

## 依存の考え方

- MineflayerやMindServer起動など、JavaScript実装が本質的に必要な部分は従来どおり維持
- それ以外の設定解決やPythonスクリプトからの起動制御は、Python側で完結する構成へ寄せる

## 補足

- この整理は、PythonコードからJavaScriptの実行経路へ直接ぶら下がっていた箇所を対象にしている
- 共有設定資産や既存のJavaScript実装全体を廃止するものではない
