import image_utility
import scene_renderer
import gaussian_blur
import grid_filter
import numpy as np
import os
import cv2

if __name__ == '__main__':
    scene_filename = './../sample.blend'
    image_filename = './../kloofendal_43d_clear_puresky_4k.hdr'
    clip_range = (512,512)
    clip_center = (0,0)
    # # bpyによるシーンの描画
    # renderer = scene_renderer.SceneRenderer(scene_filename,image_filename)
    # renderer.run()

    if not os.path.exists('./../output_color_web_mercator'):
        os.mkdir('./../output_color_web_mercator')

    if not os.path.exists('./../output_depth_web_mercator'):
        os.mkdir('./../output_depth_web_mercator')
    
    if not os.path.exists('./../output_color_web_mercator_clipped'):
        os.mkdir('./../output_color_web_mercator_clipped')

    if not os.path.exists('./../output_depth_web_mercator_clipped'):
        os.mkdir('./../output_depth_web_mercator_clipped')
    
    if not os.path.exists('./../output'):
        os.mkdir('./../output')
    
    # 出力画像の読み込み
    color_img = cv2.imread("./../output_color/image0001.png")
    # WEBメルカトルへ変換
    color_web = image_utility.ImageUtility.convert_to_web_mercator(color_img)
    # クリッピング
    color_clipped_img = image_utility.ImageUtility.clip_with_bbox(color_web,clip_center,clip_range)
    cv2.imwrite('./../output_color_web_mercator/image0001.png',color_web)
    cv2.imwrite('./../output_color_web_mercator_clipped/image0001.png',color_clipped_img)
    # 出力画像の読み込み
    depth_img = cv2.imread("./../output_depth/image0001.hdr")
    depth_web = image_utility.ImageUtility.convert_to_web_mercator(depth_img)
    # WEBメルカトルへ変換
    depth_clipped_img = image_utility.ImageUtility.clip_with_bbox(depth_web,clip_center,clip_range)
    cv2.imwrite('./../output_depth_web_mercator/image0001.hdr',depth_web)
    # クリッピング
    cv2.imwrite('./../output_depth_web_mercator_clipped/image0001.hdr',depth_clipped_img)
    # 離散格子の幅とサイズ
    delta_size = 32
    # ガウシアンの処理(中心点ごとに異なるパラメータのブラーをかける→python上でfor文?)
    # 結構重いかも(pythonのまま→cython or C++ DLL)
    # numpyでfor文関数の実行をc++側に持っていけるようにしなければいけない
    height, width,cha   = color_clipped_img.shape
    # IndexMap: 二次元のブラー入力画素値のリクエストを作成
    # 現在は、格子のため、出力そのままのリサイズ～出力画像
    index_image = np.zeros(( int(height/delta_size), int(width/delta_size), 2), dtype=np.int32)
    for y in range(0,int(height/delta_size)):
        for x in range(0,int(width/delta_size)):
            index_image[y,x,0] = min(int(x*delta_size),width)
            index_image[y,x,1] = min(int(y*delta_size),height)
    gauss_image = gaussian_blur.GaussianBlur.apply_whole_blur2d_from_depth(color_clipped_img,depth_clipped_img,index_image)
    # array.map(|x x*2|)
    # 処理を分解してnumpyのお作法に従うように変換するコスト(実装コスト)
    # →今日試せる？
    # 四角形へ変換する
    grid_img = grid_filter.GridFilter.apply_filter(gauss_image,delta_size,delta_size,0.1)
    cv2.imwrite('./../output/gauss_output.png',gauss_image) # OK
    cv2.imwrite('./../output/final_output.png',grid_img) # OK


    