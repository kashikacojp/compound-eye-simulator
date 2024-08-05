import cv2
import numpy as np
from hexagonal_filter import hexagonal_filter, hexagonal_depth_gaussian_filter, hexagonal_gaussian_filter, apply_uniform_blur
import os
import time
import OpenEXR
import array
import Imath
def load_exr_depth(filename):
    file = OpenEXR.InputFile(filename)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    depth_str = file.channel('V', Imath.PixelType(Imath.PixelType.FLOAT))
    depth_array = array.array('f', depth_str)
    depth_image = np.array(depth_array).reshape(size[1], size[0])

    return depth_image

# def update_view_process(current_image_index,image_files,depth_files,settings, image_write = True, image_show = False):
#     output_width  = settings['output_width']
#     output_height = settings['output_height']
#     start_all = time.perf_counter() # 処理時間計測
#     start = time.perf_counter() # 処理時間計測
#     panorama = cv2.imread(image_files[current_image_index])
#     depth_image = load_exr_depth(depth_files[current_image_index])
#     end   = time.perf_counter() # 処理時間計測
#     print ('load_input_images: {:.2f} ms'.format((end-start)*1000))
#     start = time.perf_counter() # 処理時間計測
#     fov = settings['interommatidial_angle'] * settings['ommatidium_count']
#     end   = time.perf_counter() # 処理時間計測
#     print ('sphere_to_plane: {:.2f} ms'.format((end-start)*1000))
#     start = time.perf_counter() # 処理時間計測
#     # フィルタサイズを計算
#     filter_size = int(settings['ommatidium_angle'] / 360 * panorama.shape[1])
    
#     if settings['debug_mode']:
#         raise NotImplementedError('debug_filter is not implemented')
#         # result_color = debug_filter(result_color, settings['ommatidium_count'], filter_size)
#         # result_depth = debug_filter(result_depth, settings['ommatidium_count'], filter_size)
#         # end = time.perf_counter() # 処理時間計測
#         # print ('debug_filter: {:.2f} ms'.format((end-start)*1000))
#     elif settings['filter'].startswith('hexagonal'):
#         if settings['filter'] == 'hexagonal':
#             result_color = hexagonal_filter(result_color, settings['ommatidium_count'], filter_size)
#         elif settings['filter'] == 'hexagonal_gaussian':
#             result_color = hexagonal_gaussian_filter(result_color, settings['ommatidium_count'], filter_size)
#         elif settings['filter'] == 'hexagonal_depth_gaussian':
#             result_color = hexagonal_depth_gaussian_filter(result_color, result_depth, settings['ommatidium_count'], filter_size)
#         end = time.perf_counter() # 処理時間計測
#         print ('color_'+settings['filter']+ ' filter: {:.2f} ms'.format((end-start)*1000))
#         start = time.perf_counter() # 処理時間計測
#         # すべての hexagonal フィルタに平滑化フィルタを適用
#         result_color = apply_uniform_blur(result_color, settings['blur_size'])
#         end = time.perf_counter() # 処理時間計測
#         print ('apply_uniform_blur: {:.2f} ms'.format((end-start)*1000))
#         start = time.perf_counter() # 処理時間計測
#         # depth 画像には hexagonal フィルタのみを適用
#         result_depth = hexagonal_filter(result_depth, settings['ommatidium_count'], filter_size)
#         end = time.perf_counter() # 処理時間計測
#         print ('depth_hexagonal_filter: {:.2f} ms'.format((end-start)*1000))

#     start = time.perf_counter() # 処理時間計測
#     # Depthイメージを可視化
#     result_depth_vis = cv2.normalize(result_depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
#     end = time.perf_counter() # 処理時間計測
#     print ('depth_visualization: {:.2f} ms'.format((end-start)*1000))
#     result_image = None
#     if image_write:
#         start = time.perf_counter() # 処理時間計測
#         # カレントディレクトリを取得
#         cur_path = os.getcwd()
#         # 出力フォルダ('/output_'+settings['filter'])が存在しない場合は作成
#         if not os.path.exists(cur_path + '/output_'+settings['filter']):
#             os.makedirs(cur_path + '/output_'+settings['filter'])
#         # 出力ファイル名は,入力ファイル名(拡張子は外す)の末尾に'_'+settings['filter']を付加
#         out_path = cur_path + '/output_'+settings['filter']
#         out_filepath = out_path + '/' + os.path.basename(image_files[current_image_index]).split('.')[0] + '_' + settings['filter'] + '.png'
#         if settings['view_mode'] == 'color':
#             result_image = result_color
#         else:
#             result_image = result_depth_vis
#         cv2.imwrite(out_filepath, result_image)
#         end=time.perf_counter()#処理時間計測
#         print('imwrite:{:.2f}ms'.format((end-start)*1000))
#     elif image_show:
#         start = time.perf_counter() # 処理時間計測
#         # 現在の表示モードに応じて表示する画像を選択
#         if settings['view_mode'] == 'color':
#             result_image = result_color
#         else:
#             result_image = result_depth_vis
#         cv2.imshow('360 Viewer', result_image)
#         end=time.perf_counter()#処理時間計測
#         print('imshow:{:.2f}ms'.format((end-start)*1000))
#     else:
#         if settings['view_mode'] == 'color':
#             result_image = result_color
#         else:
#             result_image = result_depth_vis
#     end_all=time.perf_counter()#処理時間計測
#     print('update_view:{:.2f}ms'.format((end_all-start_all)*1000))
#     return (panorama, result_image)
