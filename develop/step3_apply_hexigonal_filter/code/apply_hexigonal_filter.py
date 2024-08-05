from .update_view_process import load_exr_depth
from .hexagonal_filter    import get_hexagon_data, hexagonal_filter, hexagonal_gaussian_filter, hexagonal_depth_gaussian_filter, apply_uniform_blur
import cv2
import sys
import os
import numpy as np
import glob
import argparse
import tomllib
import math
# image_filesを返す関数
# image_filesは以下の条件を満たす2次元配列
def enumerate_image_files(image_format):
    # image_filesは以下の条件を満たす2次元配列
    # image_files[i][j]はi番目の画像のj番目の個眼の画像
    # ここで, image_fileのfilenameはimage_jjjj_iiii.(拡張子)となっている
    # ここで, iiiiは画像番号, jjjjは個眼番号
    # まず  , 最小最大の画像番号と個眼番号を求める
    min_image_number      = sys.maxsize
    max_image_number      = 0
    max_ommatidium_number = 0
    image_tmp_files       = sorted(glob.glob(image_format))
    for image_tmp_file in image_tmp_files:
        filename = os.path.basename(image_tmp_file)
        # ommatidium_numberは, filenameを'_'で分割したときの2番目の要素
        ommatidium_number = int(filename.split('_')[1])
        # image_numberは, filenameを'_'で分割したときの3番目の要素
        image_number = int(filename.split('_')[2].split('.')[0])
        max_image_number = max(max_image_number, image_number)
        min_image_number = min(min_image_number, image_number)
        max_ommatidium_number = max(max_ommatidium_number, ommatidium_number)
    # image_filesは辞書
    image_files = None
    for image_tmp_file in image_tmp_files:
        filename = os.path.basename(image_tmp_file)
        # ommatidium_numberは, filenameを'_'で分割したときの2番目の要素
        ommatidium_number = int(filename.split('_')[1])
        # image_numberは, filenameを'_'で分割したときの3番目の要素
        image_number = int(filename.split('_')[2].split('.')[0])
        # image_filesがNoneの場合, image_filesを初期化
        # キーはimage_number, 値はmax_ommatidium_number個のstring型の配列
        if image_files is None:
            image_files = {}
            image_files[image_number] = [""] * (max_ommatidium_number + 1)
        elif image_number not in image_files:
            image_files[image_number] = [""] * (max_ommatidium_number + 1)
        image_files[image_number][ommatidium_number] = image_tmp_file
    return image_files
# ここからメインプログラム
def process_frame(settings, color_image_files, depth_image_files, current_image_index):
    # 画像を読み込む
    cur_color_image_files = color_image_files[current_image_index]
    cur_depth_image_files = depth_image_files[current_image_index]
    # 六角形の取得
    output_width = settings['output_width']
    output_height = settings['output_height']
    ommatidium_count = settings['ommatidium_count']
    filter_size = settings['blur_size']
    hex_index = 0
    # 出力画像を作成
    result_color_image = np.zeros((output_height, output_width, 3), dtype=np.uint8)
    result_depth_image = np.zeros((output_height, output_width)   , dtype= np.float32)
    result_image = result_color_image
    if settings['debug_mode'] and settings['view_mode'] == 'depth':
        result_image = result_depth_image
    for center_x, center_y, hex_size, hex_points, mask in get_hexagon_data(output_width, output_height, ommatidium_count, filter_size):        # 中心座標が画像の範囲内にあることを確認
        # debug_modeの場合のみ特殊な扱いが必要
        color_image = cv2.imread( cur_color_image_files[hex_index])
        depth_image = load_exr_depth( cur_depth_image_files[hex_index])
        if 0 <= center_x < output_width and 0 <= center_y < output_height:
            if settings['debug_mode']:
                # 対象が色か深度かを判断し標的画像(target_image)に代入
                if settings['view_mode'] == 'color':
                    target_image  = color_image
                elif settings['view_mode'] == 'depth':
                    target_image = depth_image
                # 六角形のサイズを取得
                hex_width = int(hex_size * 2)
                hex_height = int(hex_size * math.sqrt(3))
                # target_imageを複製してhex_width, hex_heightにリサイズ
                target_image = cv2.resize(target_image, (hex_width, hex_height))
                # target_imageはcenter_x, center_yを中心とするhex_width, hex_heightの矩形となる
                # 次にoutput_width, output_heightの範囲に入っているmaskを取得する
                y1 = max(0, center_y - hex_height // 2)
                y2 = min(output_height, center_y + hex_height // 2)
                x1 = max(0, center_x - hex_width // 2)
                x2 = min(output_width, center_x + hex_width // 2)
                hex_mask = mask[y1:y2, x1:x2]
                # hex_regionを取得
                hex_region_y1 = y1 + hex_height // 2 - center_y
                hex_region_y2 = y2 + hex_height // 2 - center_y
                hex_region_x1 = x1 + hex_width // 2 - center_x
                hex_region_x2 = x2 + hex_width // 2 - center_x
                hex_region = target_image[hex_region_y1:hex_region_y2, hex_region_x1:hex_region_x2]
                # hex_maskを適用してhex_regionを取得
                hex_masked = cv2.bitwise_and(hex_region, hex_region, mask=hex_mask)
                # 結果画像に合成
                result_image[y1:y2, x1:x2] = cv2.add(result_image[y1:y2, x1:x2], hex_masked)
                
            else:
                if settings['filter']   == 'hexagonal':
                    result_color = hexagonal_filter(color_image, ommatidium_count, filter_size)
                elif settings['filter'] == 'hexagonal_gaussian':
                    result_color = hexagonal_gaussian_filter(color_image, ommatidium_count, filter_size)
                elif settings['filter'] == 'hexagonal_depth_gaussian':
                    result_color = hexagonal_depth_gaussian_filter(color_image, depth_image, ommatidium_count, filter_size)
                # 六角形でresultに色を埋める
                cv2.fillPoly(result_image, [hex_points], result_color)
                
        hex_index += 1

    # if not settings['debug_mode']:
    #     # 平滑化フィルタを適用
    result_image = apply_uniform_blur(result_image, settings['blur_size'])

    if settings['debug_mode'] and settings['view_mode'] == 'depth':
        # 画像の範囲を0-255に変換
        result_image = cv2.normalize(result_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # 結果を保存
    return result_image

# def debug_filter(image, ommatidium_count, filter_size):
#     return image
    
def run(settings,input_image_dir, output_image_dir,frame_index):
    # ソースディレクトリを取得
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # テスト用の色画像ファイルを読み込む
    # 現在はsrc_dir/../../step2-batch-eye-rendering/output_color/にあると仮定
    color_image_format = input_image_dir+'/*.png'
    # テスト用の深度画像ファイルを読み込む
    # 現在はsrc_dir/../../step2-batch-eye-rendering/output_depth/にあると仮定
    # .exrファイルを読み込む
    depth_image_format = color_image_format.replace('color', 'depth').replace('.png', '.exr')
    color_image_files = enumerate_image_files (color_image_format)
    depth_image_files = enumerate_image_files (depth_image_format)
    # 次にファイルをすべて表示する
    current_image_index = frame_index
    output_image = process_frame(settings, color_image_files, depth_image_files, current_image_index)
    # Call function
    # Save image to output directory
    cv2.imwrite(output_image_dir + f"/output_{current_image_index}.png", output_image)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply hexagonal filter for compound eye simulator')
    prompt = "TOML settings file (e.g., 'settings/*.toml'): "
    default = '../settings/settings.toml'
    parser.add_argument('-f','--file', type=str, default=default, help=f"{prompt} (default: {default}): ")
    args = parser.parse_args()
    with open(args.file,mode='rb') as file:
        if not file:
            print(f"Error: Could not open file {args.file}")
            exit()
        settings = tomllib.load(file)
    # デフォルト値の設定
    if not 'image_format' in settings:
        print("Warning: 'image_format' not found in settings. Using default value '../step2-batch-eye-rendering/output_color/*.png'.")
        settings['image_format'] = '../step2-batch-eye-rendering/output_color/*.png' 
    if not 'output_width' in settings: 
        print("Warning: 'output_width' not found in settings. Using default value 1920.")
        settings['output_width'] = 1920
    if not 'output_height' in settings:
        print("Warning: 'output_height' not found in settings. Using default value 1080.")
        settings ['output_height'] = 1080
    if not 'interommatidial_angle' in settings:
        settings['interommatidial_angle'] = 1.5
    if not 'ommatidium_angle' in settings:
        print("Warning: 'ommatidium_angle' not found in settings. Using default value 15.")
        settings['ommatidium_angle'] = 15
    if not 'ommatidium_count' in settings:
        print("Warning: 'ommatidium_count' not found in settings. Using default value 25.")
        settings['ommatidium_count'] = 25
    if not 'theta' in settings:
        print ("Warning: 'theta' not found in settings. Using default value 0.")
        settings['theta'] = 0
    if not 'phi' in settings:
        print ("Warning: 'phi' not found in settings. Using default value 0.")
        settings['phi'] = 0
    if not 'filter' in settings:
        print ("Warning: 'filter' not found in settings. Using default value 'hexagonal_depth_gaussian'.")
        settings['filter'] = 'hexagonal_depth_gaussian'
    if not 'view_mode' in settings:
        print( "Warning: 'view_mode' not found in settings. Using default value 'color'.")
        settings['view_mode'] = 'color'
    if not 'debug_mode' in settings:
        print ("Warning: 'debug_mode' not found in settings. Using default value False.")
        settings['debug_mode'] = False
    if not 'blur_size' in settings:
        print ("Warning: 'blur_size' not found in settings. Using default value 30.")
        settings['blur_size'] = 30
    # ソースディレクトリを取得
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # テスト用の色画像ファイルを読み込む
    # 現在はsrc_dir/../../step2-batch-eye-rendering/output_color/にあると仮定
    color_image_format = settings['image_format']
    # テスト用の深度画像ファイルを読み込む
    # 現在はsrc_dir/../../step2-batch-eye-rendering/output_depth/にあると仮定
    # .exrファイルを読み込む
    depth_image_format = color_image_format.replace('output_color', 'output_depth').replace('.png', '.exr')
    color_image_files = enumerate_image_files (color_image_format)
    depth_image_files = enumerate_image_files (depth_image_format)
    # 次にファイルをすべて表示する
    current_image_index = 0
    process_frame(settings, color_image_files, depth_image_files, current_image_index)

    
