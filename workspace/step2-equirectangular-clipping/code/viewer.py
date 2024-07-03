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
import argparse
import tomllib

def load_exr_depth(filename):
    file = OpenEXR.InputFile(filename)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    depth_str = file.channel('V', Imath.PixelType(Imath.PixelType.FLOAT))
    depth_array = array.array('f', depth_str)
    depth_image = np.array(depth_array).reshape(size[1], size[0])

    return depth_image

def create_viewer(settings):
    output_width = settings['output_width']
    output_height = settings['output_height']
    image_format = settings['image_format']
    
    # 画像の読み込み
    image_files = sorted(glob.glob(image_format))
    current_image_index = 0
    panorama = cv2.imread(image_files[current_image_index])

    # Depthファイルのパスを生成
    depth_format = image_format.replace('output_color', 'output_depth').replace('.png', '.exr')
    depth_files = sorted(glob.glob(depth_format))

    cv2.namedWindow('360 Viewer', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('360 Viewer', output_width, output_height)  # ウィンドウサイズを設定

    def update_view():
        start_all = time.perf_counter() # 処理時間計測
        start = time.perf_counter() # 処理時間計測
        nonlocal panorama
        panorama = cv2.imread(image_files[current_image_index])
        depth_image = load_exr_depth(depth_files[current_image_index])
        end   = time.perf_counter() # 処理時間計測
        print ('load_input_images: {:.2f} ms'.format((end-start)*1000))
        start = time.perf_counter() # 処理時間計測
        fov = settings['interommatidial_angle'] * settings['ommatidium_count']
        result_color = sphere_to_plane_fast(panorama, fov, settings['theta'], settings['phi'], output_width, output_height)
        result_depth = sphere_to_plane_fast(depth_image, fov, settings['theta'], settings['phi'], output_width, output_height)
        end   = time.perf_counter() # 処理時間計測
        print ('sphere_to_plane: {:.2f} ms'.format((end-start)*1000))
        start = time.perf_counter() # 処理時間計測
        # フィルタサイズを計算
        filter_size = int(settings['ommatidium_angle'] / 360 * panorama.shape[1])
        
        if settings['debug_mode']:
            result_color = debug_filter(result_color, settings['ommatidium_count'], filter_size)
            result_depth = debug_filter(result_depth, settings['ommatidium_count'], filter_size)
            end = time.perf_counter() # 処理時間計測
            print ('debug_filter: {:.2f} ms'.format((end-start)*1000))
        elif settings['filter'].startswith('hexagonal'):
            if settings['filter'] == 'hexagonal':
                result_color = hexagonal_filter(result_color, settings['ommatidium_count'], filter_size)
            elif settings['filter'] == 'hexagonal_gaussian':
                result_color = hexagonal_gaussian_filter(result_color, settings['ommatidium_count'], filter_size)
            elif settings['filter'] == 'hexagonal_depth_gaussian':
                result_color = hexagonal_depth_gaussian_filter(result_color, result_depth, settings['ommatidium_count'], filter_size)
            end = time.perf_counter() # 処理時間計測
            print ('color_'+settings['filter']+ ' filter: {:.2f} ms'.format((end-start)*1000))
            start = time.perf_counter() # 処理時間計測
            # すべての hexagonal フィルタに平滑化フィルタを適用
            result_color = apply_uniform_blur(result_color, settings['blur_size'])
            end = time.perf_counter() # 処理時間計測
            print ('apply_uniform_blur: {:.2f} ms'.format((end-start)*1000))
            start = time.perf_counter() # 処理時間計測
            # depth 画像には hexagonal フィルタのみを適用
            result_depth = hexagonal_filter(result_depth, settings['ommatidium_count'], filter_size)
            end = time.perf_counter() # 処理時間計測
            print ('depth_hexagonal_filter: {:.2f} ms'.format((end-start)*1000))

        start = time.perf_counter() # 処理時間計測
        # Depthイメージを可視化
        result_depth_vis = cv2.normalize(result_depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        end = time.perf_counter() # 処理時間計測
        print ('depth_visualization: {:.2f} ms'.format((end-start)*1000))
        start = time.perf_counter() # 処理時間計測
        # 現在の表示モードに応じて表示する画像を選択
        if settings['view_mode'] == 'color':
            cv2.imshow('360 Viewer', result_color)
        else:
            cv2.imshow('360 Viewer', result_depth_vis)
        end = time.perf_counter() # 処理時間計測
        print ('imshow: {:.2f} ms'.format((end-start)*1000))
        end_all = time.perf_counter() # 処理時間計測
        print ('update_view: {:.2f} ms'.format((end_all-start_all)*1000))

    def print_info(message):
        print(message)

    # 初期表示
    update_view()
    print_info("Viewer started. Use WASD to navigate, 1/2 for interommatidial angle, 3/4 for ommatidium count, 5/6 for ommatidium angle, F to toggle filter, Z to switch between color and depth view.")

    while True:
        key = cv2.waitKey(1) & 0xFF  # キー入力を待機

        if key == ord('f'):
            if settings['filter'] == 'none':
                settings['filter'] = 'hexagonal'
            elif settings['filter'] == 'hexagonal':
                settings['filter'] = 'hexagonal_gaussian'
            elif settings['filter'] == 'hexagonal_gaussian':
                settings['filter'] = 'hexagonal_depth_gaussian'
            else:
                settings['filter'] = 'none'
            print_info(f"Key: F - Toggle filter: {settings['filter']}")
            update_view()
        elif key == ord('x'):
            settings['debug_mode'] = not settings['debug_mode']
            print_info(f"Key: X - Toggle debug mode: {'on' if settings['debug_mode'] else 'off'}")
            update_view()
        if key == ord('z'):
            settings['view_mode'] = 'depth' if settings['view_mode'] == 'color' else 'color'
            print_info(f"Key: Z - Switch to {settings['view_mode']} view")
            update_view()
        elif key == ord('1'):
            settings['interommatidial_angle'] = max(settings['interommatidial_angle'] - 0.1, 0.1)
            print_info(f"Key: 1 - Decrease interommatidial angle to {settings['interommatidial_angle']:.1f}")
            update_view()
        elif key == ord('2'):
            settings['interommatidial_angle'] = min(settings['interommatidial_angle'] + 0.1, 10)
            print_info(f"Key: 2 - Increase interommatidial angle to {settings['interommatidial_angle']:.1f}")
            update_view()
        elif key == ord('3'):
            settings['ommatidium_count'] = max(settings['ommatidium_count'] - 1, 1)
            print_info(f"Key: 3 - Decrease ommatidium count to {settings['ommatidium_count']}")
            update_view()
        elif key == ord('4'):
            settings['ommatidium_count'] = min(settings['ommatidium_count'] + 1, 36)
            print_info(f"Key: 4 - Increase ommatidium count to {settings['ommatidium_count']}")
            update_view()
        elif key == ord('5'):
            settings['ommatidium_angle'] = max(settings['ommatidium_angle'] - 1, 0.1)
            print_info(f"Key: 5 - Decrease ommatidium angle to {settings['ommatidium_angle']:.1f}")
            update_view()
        elif key == ord('6'):
            settings['ommatidium_angle'] = min(settings['ommatidium_angle'] + 1, 50)
            print_info(f"Key: 6 - Increase ommatidium angle to {settings['ommatidium_angle']:.1f}")
            update_view()
        elif key == ord('w'):
            settings['phi'] = min(settings['phi'] + 5, 90)
            print_info(f"Key: W - Rotate up, Phi: {settings['phi']}")
            update_view()
        elif key == ord('s'):
            settings['phi'] = max(settings['phi'] - 5, -90)
            print_info(f"Key: S - Rotate down, Phi: {settings['phi']}")
            update_view()
        elif key == ord('a'):
            settings['theta'] = (settings['theta'] + 10) % 360
            print_info(f"Key: A - Rotate left, Theta: {settings['theta']}")
            update_view()
        elif key == ord('d'):
            settings['theta'] = (settings['theta'] - 10) % 360
            print_info(f"Key: D - Rotate right, Theta: {settings['theta']}")
            update_view()
        elif key == ord('['):  # [キー
            current_image_index = (current_image_index - 1) % len(image_files)
            print_info(f"Key: [ - Previous image, Index: {current_image_index}")
            update_view()
        elif key == ord(']'):  # ]キー
            current_image_index = (current_image_index + 1) % len(image_files)
            print_info(f"Key: ] - Next image, Index: {current_image_index}")
            update_view()
        elif key == ord('}'):  # Shift+]
            current_image_index = (current_image_index + 10) % len(image_files)
            print_info(f"Key: Shift+] - Forward 10 frames, Index: {current_image_index}")
            update_view()
        elif key == ord('{'):  # Shift+[
            current_image_index = (current_image_index - 10) % len(image_files)
            print_info(f"Key: Shift+[ - Backward 10 frames, Index: {current_image_index}")
            update_view()
        elif key == 27:  # ESCキー
            print_info("Key: ESC - Quit the viewer")
            break
        elif key == ord('b'):
            settings['blur_size'] = (settings['blur_size'] % 50) + 1
            print_info(f"Key: B - Set blur size: {settings['blur_size']}")
            update_view()
    cv2.destroyAllWindows()
    return settings

def get_input_with_default(prompt, default):
    user_input = input(f"{prompt} (default: {default}): ")
    return int(user_input) if user_input else default

if __name__ == "__main__":
    # argparserの設定
    parser = argparse.ArgumentParser(description='360 Viewer for compound eye simulator')
    prompt = "TOML settings file (e.g., 'settings/*.toml'): "
    default = './settings/settings.toml'
    parser.add_argument('-f','--file', type=str, default=default, help=f"{prompt} (default: {default}): ")
    args = parser.parse_args()
    with open(args.file,mode='rb') as file:
        if not file:
            print(f"Error: Could not open file {args.file}")
            exit()
        settings = tomllib.load(file)
    # デフォルト値の設定
    if not 'image_format' in settings:
        print("Warning: 'image_format' not found in settings. Using default value '../step1-panorama-rendering/output_color/*.png'.")
        settings['image_format'] = '../step1-panorama-rendering/output_color/*.png' 
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
    
    # ビューアーの作成
    final_settings = create_viewer(settings)

    print("Final settings:", final_settings)