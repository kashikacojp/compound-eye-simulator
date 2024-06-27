import cv2
import numpy as np
from sphere_to_plane import sphere_to_plane_fast
from hexagonal_filter import hexagonal_filter, debug_filter, hexagonal_depth_gaussian_filter, hexagonal_gaussian_filter, apply_uniform_blur
import glob
import os
import OpenEXR
import Imath
import array
import time

def load_exr_depth(filename):
    file = OpenEXR.InputFile(filename)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    depth_str = file.channel('V', Imath.PixelType(Imath.PixelType.FLOAT))
    depth_array = array.array('f', depth_str)
    depth_image = np.array(depth_array).reshape(size[1], size[0])

    return depth_image

def create_viewer(settings):
    # 画像の読み込み
    image_files = sorted(glob.glob(settings['image_format']))
    current_image_index = 0
    panorama = cv2.imread(image_files[current_image_index])

    # Depthファイルのパスを生成
    depth_format = settings['image_format'].replace('output_color', 'output_depth').replace('.png', '.exr')
    depth_files = sorted(glob.glob(depth_format))

    def update_view():
        nonlocal panorama
        panorama = cv2.imread(image_files[current_image_index])
        depth_image = load_exr_depth(depth_files[current_image_index])

        fov = settings['interommatidial_angle'] * settings['ommatidium_count']
        result_color = sphere_to_plane_fast(panorama, fov, settings['theta'], settings['phi'], settings['output_width'], settings['output_height'])
        result_depth = sphere_to_plane_fast(depth_image, fov, settings['theta'], settings['phi'], settings['output_width'], settings['output_height'])
        
        # フィルタサイズを計算
        filter_size = int(settings['ommatidium_angle'] / 360 * panorama.shape[1])
        
        if settings['debug_mode']:
            result_color = debug_filter(result_color, settings['ommatidium_count'], filter_size)
            result_depth = debug_filter(result_depth, settings['ommatidium_count'], filter_size)
        elif settings['filter'].startswith('hexagonal'):
            if settings['filter'] == 'hexagonal':
                result_color = hexagonal_filter(result_color, settings['ommatidium_count'], filter_size)
            elif settings['filter'] == 'hexagonal_gaussian':
                result_color = hexagonal_gaussian_filter(result_color, settings['ommatidium_count'], filter_size)
            elif settings['filter'] == 'hexagonal_depth_gaussian':
                result_color = hexagonal_depth_gaussian_filter(result_color, result_depth, settings['ommatidium_count'], filter_size)
            
            # すべての hexagonal フィルタに平滑化フィルタを適用
            result_color = apply_uniform_blur(result_color, settings['blur_size'])
            
            # depth 画像には hexagonal フィルタのみを適用
            result_depth = hexagonal_filter(result_depth, settings['ommatidium_count'], filter_size)

        
        # Depthイメージを可視化
        result_depth_vis = cv2.normalize(result_depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        # カレントディレクトリを取得
        cur_path = os.getcwd()
        # 出力フォルダ('/output_'+settings['filter'])が存在しない場合は作成
        if not os.path.exists(cur_path + '/output_'+settings['filter']):
            os.makedirs(cur_path + '/output_'+settings['filter'])
        # 出力ファイル名は,入力ファイル名(拡張子は外す)の末尾に'_'+settings['filter']を付加
        out_path = cur_path + '/output_'+settings['filter']
        out_filepath = out_path + '/' + os.path.basename(image_files[current_image_index]).split('.')[0] + '_' + settings['filter'] + '.png'
        
        # 現在の表示モードに応じて表示する画像を選択
        if settings['view_mode'] == 'color':
            cv2.imwrite(out_filepath, result_color)
        else:
            cv2.imwrite(out_filepath, result_depth_vis)

    for i in range(len(image_files)):
        current_image_index = i
        print(f"Index: {i}")
        update_view()
    return settings

def show_settings(settings):
    print("Settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    settings = {
        'output_width': 1920,
        'output_height': 1080,
        'image_format': '../step1-panorama-rendering/output_color/*.png',
        'interommatidial_angle': 1.5,  # 個眼間角度の初期値
        'ommatidium_angle': 15,  # 個眼視野角の初期値
        'ommatidium_count': 25,  # 個眼個数の初期値
        'theta': 0,
        'phi': 0,
        'filter': 'none',  # フィルタの初期設定
        'view_mode': 'color',  # 表示モードの初期設定
        'debug_mode': False,  # デバッグモードの初期設定
        'blur_size': 30  # ブラーサイズの初期値
    }
    show_settings(settings)
    final_settings = create_viewer(settings)

    print("Final settings:", final_settings)