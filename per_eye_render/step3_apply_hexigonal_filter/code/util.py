import os
import cv2

def imread(path):
    tmp_dir = os.getcwd()
    # 1. 対象ファイルがあるディレクトリに移動
    if len(path.split("/")) > 1:
        file_dir = "/".join(path.split("/")[:-1])
        os.chdir(file_dir)
    # 2. 対象ファイルの名前を変更
    tmp_name = "tmp_name"
    os.rename(path.split("/")[-1], tmp_name)
    # 3. 対象ファイルを読み取る
    img = cv2.imread(tmp_name)
    # 4. 対象ファイルの名前を戻す
    os.rename(tmp_name, path.split("/")[-1])
    # カレントディレクトリをもとに戻す
    os.chdir(tmp_dir)
    return img

def imwrite(path, img): # cv2は日本語パスに対応しないため特殊対応
    tmp_dir = os.getcwd()
    # 1. 保存するディレクトリに移動
    if len(path.split("/")) > 1:
        file_dir = "/".join(path.split("/")[:-1])
        os.chdir(file_dir)
    # 2. 対象ファイルを保存
    tmp_name = "tmp_name.png"
    cv2.imwrite(tmp_name, img)
    # 3. 対象ファイルの名前を戻す
    if os.path.exists(path.split("/")[-1]):  # ファイルが既にあれば削除
        os.remove(path.split("/")[-1])
    os.rename(tmp_name, path.split("/")[-1])
    # カレントディレクトリをもとに戻す
    os.chdir(tmp_dir)