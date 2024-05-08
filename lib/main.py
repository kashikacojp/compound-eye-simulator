import image_utility
import scene_renderer
import cv2
import os

if __name__ == '__main__':
    scene_filename = './../sample.blend'
    image_filename = './../kloofendal_43d_clear_puresky_4k.hdr'
    clip_range     = (512,512)
    clip_center    = (0,0)
    # bpyによるシーンの描画
    renderer = scene_renderer.SceneRenderer(scene_filename,image_filename)
    renderer.run()

    if not os.path.exists('./../output_color_web_mercator'):
        os.mkdir('./../output_color_web_mercator')

    if not os.path.exists('./../output_depth_web_mercator'):
        os.mkdir('./../output_depth_web_mercator')
    
    if not os.path.exists('./../output_color_web_mercator_clipped'):
        os.mkdir('./../output_color_web_mercator_clipped')

    if not os.path.exists('./../output_depth_web_mercator_clipped'):
        os.mkdir('./../output_depth_web_mercator_clipped')
    
    # 出力画像の読み込み
    color_img = cv2.imread("./../output_color/image0001.png")
    # WEBメルカトルへ変換
    color_web = image_utility.ImageUtility.convert_to_web_mercator(color_img)
    # クリッピング
    color_clipped_img = image_utility.ImageUtility.clip_with_bbox(color_web,clip_center,clip_range)
    cv2.imwrite('./../output_color_web_mercator/image0001.png',color_web)
    cv2.imwrite('./../output_color_web_mercator_clipped/image0001.png',color_clipped_img)
    # 出力画像の読み込み
    depth_img = cv2.imread("./../output_depth/image0001.png")
    depth_web = image_utility.ImageUtility.convert_to_web_mercator(depth_img)
    # WEBメルカトルへ変換
    depth_clipped_img = image_utility.ImageUtility.clip_with_bbox(depth_web,clip_center,clip_range)
    cv2.imwrite('./../output_depth_web_mercator/image0001.png',depth_web)
    # クリッピング
    cv2.imwrite('./../output_depth_web_mercator_clipped/image0001.png',depth_clipped_img)
    