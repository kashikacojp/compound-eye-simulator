import cv2
import numpy as np
from sphere_to_plane import sphere_to_plane_fast
from hexagonal_filter import hexagonal_filter, debug_filter, hexagonal_depth_gaussian_filter, hexagonal_gaussian_filter, apply_uniform_blur
from update_view_process import update_view_process
import glob
import argparse
import tomllib

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
        (tmp_panorama,_)  = update_view_process(current_image_index, image_files, depth_files, settings,True,False)
        panorama = tmp_panorama
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
    
    show_settings(settings)
    final_settings = create_viewer(settings)

    print("Final settings:", final_settings)