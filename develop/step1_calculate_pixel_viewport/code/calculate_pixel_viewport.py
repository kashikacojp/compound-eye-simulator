import tomllib
import argparse
import math
# まず画面上における六角形のサイズを求める
def get_hexagon_data(width, height, ommatidium_count):
    centers = []
    # 六角形のサイズを計算
    hex_size = width / (ommatidium_count * math.sqrt(3))
    # 縦の六角形の数を計算
    vertical_count = int(height / (hex_size * 1.5))
    for row in range(vertical_count + 1):
        for col in range(ommatidium_count + 1):
            # 六角形の中心座標を計算
            center_x = int((col + (row % 2) * 0.5) * hex_size * math.sqrt(3))
            center_y = int(row * hex_size * 1.5)
            # 中心座標が画像の範囲内にある場合のみ処理を続ける
            if 0 <= center_x < width and 0 <= center_y < height:
                centers.append((center_x, center_y))
    return (hex_size, vertical_count, centers)

def calc_pixel_viewport(settings):
    width  = settings['output_width']
    height = settings['output_height']
    ommatidium_count = settings['ommatidium_count']
    (hex_size, vertical_count, centers) = get_hexagon_data(width, height, ommatidium_count)
    # 個眼間角度を求める
    interommatidial_angle = settings['interommatidial_angle']
    # 個眼全体の角度を求める
    sum_ommatidial_angle = interommatidial_angle * ommatidium_count
    # centersの座標系を画面の真ん中が(0,0)になるように変換
    for i in range(len(centers)):
        centers[i] = (centers[i][0] - width/2, centers[i][1] - height/2)
    # 左端が-sum_ommatidial_angle/2, 右端が+sum_ommatidial_angle/2になるように変換
    # これを個眼の中心座標とする
    for i in range(len(centers)):
        centers[i] = (centers[i][0] * sum_ommatidial_angle / width, centers[i][1] * sum_ommatidial_angle / width)
    # bpyの描画時に必要な情報を辞書形式でまとめる
    # 球面上の各個眼に対応する六角形の中心座標をcentersに格納
    # 画面の中心座標(theta,phi)
    # 個眼視野角(ommatidium_angle)
    final_settings = { 'centers': centers, 'theta': settings['theta'], 'phi': settings['phi'], 'ommatidium_angle': settings['ommatidium_angle'] }
    return final_settings


def run(settings):
    return calc_pixel_viewport(settings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate pixel viewport for compound eye simulator')
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
    # 中心座標の設定を計算
    final_settings = calc_pixel_viewport(settings)
    # bpyにコピペして動作するようにpython辞書の形式で表示
    # 変数名はinput_settingsとする
    print('\n')
    print("input_settings = {")
    for key, value in final_settings.items():
        print(f"    '{key}': {value},")
    print("}")