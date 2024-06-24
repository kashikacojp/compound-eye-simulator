import cv2
import numpy as np
from sphere_to_plane import sphere_to_plane_fast
from hexagonal_filter import hexagonal_filter, debug_filter, hexagonal_depth_gaussian_filter, hexagonal_gaussian_filter, apply_uniform_blur
import glob
import os

def create_viewer(output_width, output_height, image_format):
    # 画像の読み込み
    image_files = sorted(glob.glob(image_format))
    current_image_index = 0
    panorama = cv2.imread(image_files[current_image_index])

    # Depthファイルのパスを生成
    depth_format = image_format.replace('output_color', 'output_depth')
    depth_files = sorted(glob.glob(depth_format))

    settings = {
        'interommatidial_angle': 5,  # 個眼間角度の初期値
        'ommatidium_angle': 5,  # 個眼視野角の初期値
        'ommatidium_count': 18,  # 個眼個数の初期値
        'theta': 0,
        'phi': 0,
        'filter': 'none',  # フィルタの初期設定
        'view_mode': 'color',  # 表示モードの初期設定
        'debug_mode': False,  # デバッグモードの初期設定
        'blur_size': 30  # ブラーサイズの初期値 (追加)
    }


    cv2.namedWindow('360 Viewer', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('360 Viewer', output_width, output_height)  # ウィンドウサイズを設定

    def update_view():
        nonlocal panorama
        panorama = cv2.imread(image_files[current_image_index])
        depth_image = cv2.imread(depth_files[current_image_index], cv2.IMREAD_ANYDEPTH)

        fov = settings['interommatidial_angle'] * settings['ommatidium_count']
        result_color = sphere_to_plane_fast(panorama, fov, settings['theta'], settings['phi'], output_width, output_height)
        result_depth = sphere_to_plane_fast(depth_image, fov, settings['theta'], settings['phi'], output_width, output_height)
        
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
        #result_depth_vis = cv2.applyColorMap(result_depth_vis, cv2.COLORMAP_JET)
        
        # 現在の表示モードに応じて表示する画像を選択
        if settings['view_mode'] == 'color':
            cv2.imshow('360 Viewer', result_color)
        else:
            cv2.imshow('360 Viewer', result_depth_vis)

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
        elif key == ord('d'):
            settings['theta'] = (settings['theta'] - 10) % 360
            print_info(f"Key: A - Rotate left, Theta: {settings['theta']}")
            update_view()
        elif key == ord('a'):
            settings['theta'] = (settings['theta'] + 10) % 360
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
    # デフォルトの解像度を設定
    default_width = 1920
    default_height = 1080

    # 出力解像度を設定（デフォルト値付き）
    output_width = get_input_with_default("Enter output width", default_width)
    output_height = get_input_with_default("Enter output height", default_height)
    image_format = get_input_with_default("Enter image format (e.g., 'images/*.png'): ", 'D:/Work/KASHIKA/Develop/compound-eye-simulator/Flower/jim/workflow/step1-panorama-rendering/output_color/*.png')
    
    final_settings = create_viewer(output_width, output_height, image_format)

    print("Final settings:", final_settings)