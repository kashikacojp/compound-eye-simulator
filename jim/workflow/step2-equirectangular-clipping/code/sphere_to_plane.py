import cv2
import numpy as np

def sphere_to_plane_fast(image, fov, theta, phi, out_width, out_height):
    height, width = image.shape[:2]
    
    # fovの上限を設定し、ラジアンに変換
    fov = min(fov, 179)
    fov_rad = np.deg2rad(fov)
    theta_rad = np.deg2rad(theta)
    phi_rad = np.deg2rad(phi)
    
    # 座標グリッドを作成
    x, y = np.meshgrid(np.arange(out_width), np.arange(out_height))
    
    # スクリーン座標を -1 から 1 の範囲に正規化
    x = (x - out_width / 2) / (out_width / 2)
    y = (out_height / 2 - y) / (out_height / 2)
    
    # 安全なtan計算を使用して視線ベクトルを計算
    tan_fov = np.tan(fov_rad / 2)
    camera_x = tan_fov * x
    camera_y = tan_fov * y
    camera_z = -np.ones_like(x)
    
    # カメラの回転を適用
    rot_x = camera_x * np.cos(theta_rad) + camera_z * np.sin(theta_rad)
    rot_y = camera_y * np.cos(phi_rad) - (-camera_x * np.sin(theta_rad) + camera_z * np.cos(theta_rad)) * np.sin(phi_rad)
    rot_z = camera_y * np.sin(phi_rad) + (-camera_x * np.sin(theta_rad) + camera_z * np.cos(theta_rad)) * np.cos(phi_rad)
    
    # 球面座標に変換
    theta = np.arctan2(rot_x, -rot_z)
    phi = np.arctan2(rot_y, np.sqrt(rot_x**2 + rot_z**2))
    
    # 360度画像上の座標を計算
    source_x = ((theta / (2 * np.pi) + 0.5) * width) % width
    source_y = (1 - (phi / np.pi + 0.5)) * height
    
    # 座標を適切な範囲に制限
    source_x = np.clip(source_x, 0, width - 1)
    source_y = np.clip(source_y, 0, height - 1)
    
    # OpenCVのremap関数を使用して高速に画像をマッピング
    map_x = source_x.astype(np.float32)
    map_y = source_y.astype(np.float32)
    out_image = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)
    
    return out_image