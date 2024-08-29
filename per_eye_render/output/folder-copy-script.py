import os
import shutil

def copy_images_flat(root_path):
    # 新しいフォルダ名を作成（接頭辞 "tmp_" を追加）
    new_folder = f"tmp_{os.path.basename(root_path)}"
    
    # 新しいフォルダを作成
    os.makedirs(new_folder, exist_ok=True)
    
    # コピーされたファイル数を追跡
    copied_count = 0
    
    # root_path内のすべてのサブフォルダを走査
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            # 画像ファイルのみを処理（.pngファイル）かつ "debug" を含まないファイル
            if filename.lower().endswith('.png') and "debug" not in filename:
                # 元のファイルのフルパス
                src_file = os.path.join(dirpath, filename)
                
                # 新しいファイルのフルパス
                dst_file = os.path.join(new_folder, filename)
                
                # ファイルをコピー
                shutil.copy2(src_file, dst_file)
                copied_count += 1
    
    print(f"画像のコピーが完了しました。新しいフォルダ: {new_folder}")
    print(f"コピーされたファイル数: {copied_count}")

# 使用例
if __name__ == "__main__":
    root_path = "radius=0.005"  # ここに実際のルートパスを指定してください
    copy_images_flat(root_path)

    root_path = "radius=0.0"  # ここに実際のルートパスを指定してください
    copy_images_flat(root_path)
