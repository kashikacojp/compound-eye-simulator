# 環境設定
## Pythonのインストール
1. Python 3.11.9をユーザ向けにインストール
- リンク：[https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)
2. 環境変数**PATH**に以下の二つを追加
```
1. python.exeインストールフォルダ
例）C:\Users\[ユーザ名]\AppData\Local\Programs\Python\Python311
2. pythonのScriptsフォルダ
例）C:\Users\[ユーザ名]\AppData\Local\Programs\Python\Python311\Scripts
```
3. 本フォルダ内で以下コマンドを実行
```
python -m pip install -r requirements.txt
```

# データ準備
## Blenderファイルの用意
1. 使用するBlenderファイルを用意する（別途共有されている場合は、ダウンロードして任意の場所に配置）

## 設定ファイルを自分の環境用に書き換え
1. 同梱の**settings.toml** を開く
2. `scene_path =` に参照するBlenderファイルへのパスを書く。 ※区切り文字は「\」ではなく、「/」を使用。

## パノラマ画像を配置
1. レンダリング済みのパノラマ画像を用意する（別途共有されている場合は、ダウンロード）
2. カラー画像とデプス画像を以下の場所に配置
    - カラー画像：compound-eye-simulator\panorama_render\step1-panorama-rendering\output_color
    - デプス画像：compound-eye-simulator\panorama_render\step1-panorama-rendering\output_depth

# 使い方
## ビューア
- **ui_viewer.bat** をダブルクリック

## 個眼ごとレンダリング
- ビューアから使う場合
    - ビューアの画面上で **個眼毎にレンダリング** ボタンをクリック
- 1枚の画像を描画する場合
    - コマンドプロンプトを開く
    - **compound-eye-simulator\per_eye_render** フォルダに移動
    - 以下のコマンドを実行
```
python render.py --setting [settingファイルの場所]\setting.toml
```
- 連番画像をすべて描画する場合
    - コマンドプロンプトを開く
    - **compound-eye-simulator\per_eye_render** フォルダに移動
    - 以下のコマンドを実行（1フレーム目から10フレーム目の場合）
```
python render.py --setting [settingファイルの場所]\setting.toml --animation_start 1 --animation_end 10
```
