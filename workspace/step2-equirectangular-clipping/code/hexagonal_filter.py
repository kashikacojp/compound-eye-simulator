import cv2
import numpy as np
import math

def hexagon_corners(center, size):
    x, y = center
    w = math.sqrt(3) * size
    h = 2 * size

    return np.array([
        [x - w / 2, y - h / 4],
        [x, y - h / 2],
        [x + w / 2, y - h / 4],
        [x + w / 2, y + h / 4],
        [x, y + h / 2],
        [x - w / 2, y + h / 4]
    ], dtype=np.int32)

def get_hexagon_data(image, ommatidium_count, filter_size):
    height, width = image.shape[:2]
    
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
                # 六角形の頂点を計算
                hex_points = hexagon_corners((center_x, center_y), hex_size)

                # マスクを作成
                mask = np.zeros((height, width), dtype=np.uint8)
                cv2.fillPoly(mask, [hex_points], 255)

                # 入力画像から参照範囲を抽出
                ref_image = cv2.getRectSubPix(image, (filter_size, filter_size), (center_x, center_y))

                yield center_x, center_y, hex_size, hex_points, mask, ref_image

def hexagonal_filter(image, ommatidium_count, filter_size):
    height, width = image.shape[:2]
    result = np.zeros_like(image)

    for center_x, center_y, hex_size, hex_points, mask, ref_image in get_hexagon_data(image, ommatidium_count, filter_size):
        # 参照画像の平均色を計算
        avg_color = cv2.mean(ref_image)[:3]

        # 六角形を平均色で塗りつぶす
        cv2.fillPoly(result, [hex_points], avg_color)

    return result

def hexagonal_gaussian_filter(image, ommatidium_count, filter_size):
    height, width = image.shape[:2]
    result = np.zeros_like(image)

    for center_x, center_y, hex_size, hex_points, mask, _ in get_hexagon_data(image, ommatidium_count, filter_size):
        # ガウシアンカーネルを作成
        gaussian_kernel = cv2.getGaussianKernel(filter_size, -1)
        gaussian_kernel = gaussian_kernel * gaussian_kernel.T

        # 入力画像から参照範囲を抽出
        ref_image = cv2.getRectSubPix(image, (filter_size, filter_size), (center_x, center_y))

        # ガウシアンフィルタを適用
        filtered_image = cv2.filter2D(ref_image, -1, gaussian_kernel)

        # フィルタリングされた画像の平均色を計算
        avg_color = cv2.mean(filtered_image)[:3]

        # 六角形を平均色で塗りつぶす
        cv2.fillPoly(result, [hex_points], avg_color)

    return result

def hexagonal_depth_gaussian_filter(image, depth_image, ommatidium_count, max_filter_size):
    height, width = image.shape[:2]
    result = np.zeros_like(image)

    # Depthの最小値と最大値を取得
    depth_min = np.min(depth_image)
    depth_max = np.max(depth_image)
    print("DEBUG: hexagonal_depth_gaussian_filter: depth_min = {}, depth_max = {}", depth_min, depth_max)

    for center_x, center_y, hex_size, hex_points, mask, _ in get_hexagon_data(image, ommatidium_count, max_filter_size):
        # 中心座標が画像の範囲内にあることを確認
        if 0 <= center_x < width and 0 <= center_y < height:
            # Depthに基づいてfilter_sizeを計算
            depth_value = depth_image[center_y, center_x]
            depth_value = np.clip(depth_value, 0, 100.0)
            depth_ratio = depth_value / 100.0
            filter_size = max(int(depth_ratio * max_filter_size), 1)

            # ガウシアンカーネルを作成
            gaussian_kernel = cv2.getGaussianKernel(filter_size, -1)
            gaussian_kernel = gaussian_kernel * gaussian_kernel.T

            # 入力画像から参照範囲を抽出
            ref_image = cv2.getRectSubPix(image, (filter_size, filter_size), (center_x, center_y))

            # ガウシアンフィルタを適用
            filtered_image = cv2.filter2D(ref_image, -1, gaussian_kernel)

            # フィルタリングされた画像の平均色を計算
            avg_color = cv2.mean(filtered_image)[:3]

            # 六角形を平均色で塗りつぶす
            cv2.fillPoly(result, [hex_points], avg_color)

    return result

def debug_filter(image, ommatidium_count, filter_size):
    height, width = image.shape[:2]
    result = np.zeros_like(image)

    for center_x, center_y, hex_size, hex_points, mask, ref_image in get_hexagon_data(image, ommatidium_count, filter_size):
        # 参照画像を六角形内にリサイズしてマッピング
        hex_width = int(hex_size * 2)
        hex_height = int(hex_size * math.sqrt(3))
        hex_image = cv2.resize(ref_image, (hex_width, hex_height))
        
        # 六角形領域を切り出す
        y1 = max(0, center_y - hex_height // 2)
        y2 = min(height, center_y + hex_height // 2)
        x1 = max(0, center_x - hex_width // 2)
        x2 = min(width, center_x + hex_width // 2)
        
        hex_mask = mask[y1:y2, x1:x2]
        hex_region = hex_image[:y2-y1, :x2-x1]
        
        # マスクを適用して六角形領域を切り出し
        hex_masked = cv2.bitwise_and(hex_region, hex_region, mask=hex_mask)

        # 結果画像に合成
        result[y1:y2, x1:x2] = cv2.add(result[y1:y2, x1:x2], hex_masked)

    return result

def apply_uniform_blur(image, blur_size):
    """
    画像全体に均一に平滑化フィルタをかける関数
    
    :param image: 入力画像
    :param blur_size: ブラーカーネルのサイズ（奇数）
    :return: 平滑化された画像
    """
    # blur_sizeが偶数の場合、奇数に調整
    if blur_size % 2 == 0:
        blur_size += 1
    
    # kernel = np.ones((blur_size, blur_size), np.float32) / (blur_size * blur_size)
    #return cv2.filter2D(image, -1, kernel)
    return cv2.GaussianBlur(image, (blur_size, blur_size), 0)