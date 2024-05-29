import image_utility
import scene_renderer
import gaussian_blur
import grid_filter
import hex_filter
import numpy as np
import os
import cv2
import sys

if __name__ == '__main__':
    # コマンドライン引数の処理
    # シーンのファイル名、出力画像のファイル名、出力ディレクトリ, モードを取得
    scene_filename = None
    image_filename = None
    out_dir        = None
    mode           = None
    skip_render    = False
    # シーンのファイル名をコマンドライン引数から取得
    for i in range(1,len(sys.argv)):
        if sys.argv[i] == '-s':
            if i+1 >= len(sys.argv):
                print('Error: -s option requires an argument')
                sys.exit(1)
            scene_filename = sys.argv[i+1]
        if sys.argv[i] == '-i':
            if i+1 >= len(sys.argv):
                print('Error: -i option requires an argument')
                sys.exit(1)
            image_filename = sys.argv[i+1]
        if sys.argv[i] == '-o':
            if i+1 >= len(sys.argv):
                print('Error: -o option requires an argument')
                sys.exit(1)
            out_dir = sys.argv[i+1]
        if sys.argv[i] == '-m':
            if i+1 >= len(sys.argv):
                print('Error: -m option requires an argument')
                sys.exit(1)
            mode = sys.argv[i+1]
        if sys.argv[i] == '--skip-render':
            skip_render = True
    
    if not scene_filename:
        scene_filename = './../Flower/flower.blend'
    if not image_filename:
        image_filename = './../symmetrical_garden_02_4k.hdr'
    if not out_dir:
        out_dir = './../output'
    if not mode:
        mode = 'Hex'

    if skip_render != True:
        if not os.path.exists(scene_filename):
            raise Exception('Scene file does not exist')
        if not os.path.exists(image_filename):
            raise Exception('Image file does not exist')

    if not os.path.exists(out_dir):
        raise Exception('Output directory does not exist')

    if not os.path.exists(out_dir+'/temp'):
        os.mkdir(out_dir+'/temp')

    if not os.path.exists(out_dir+'/temp/color'):
        os.mkdir(out_dir+'/temp/color')
    
    if not os.path.exists(out_dir+'/temp/depth'):
        os.mkdir(out_dir+'/temp/depth')

    if not os.path.exists(out_dir+'/temp/color_web_mercator'):
        os.mkdir(out_dir+'/temp/color_web_mercator')

    if not os.path.exists(out_dir+'/temp/depth_web_mercator'):
        os.mkdir(out_dir+'/temp/depth_web_mercator')
    
    if not os.path.exists(out_dir+'/temp/color_web_mercator_clipped'):
        os.mkdir(out_dir+'/temp/color_web_mercator_clipped')

    if not os.path.exists(out_dir+'/temp/depth_web_mercator_clipped'):
        os.mkdir(out_dir+'/temp/depth_web_mercator_clipped')
    
    if not os.path.exists(out_dir+'/result'):
        os.mkdir(out_dir+'/result')


    clip_range = (512,512)
    clip_center = (0,0)
    # bpyによるシーンの描画

    renderer_output_color_format = 'PNG'
    renderer_output_depth_format = 'PNG'

    if not skip_render:
        renderer = scene_renderer.SceneRenderer(
            scene_filename,
            image_filename, 
            output_path=out_dir+'/temp',
            output_color_path=out_dir+'/temp/color',
            output_depth_path=out_dir+'/temp/depth'
        )
        renderer.run()
        renderer_output_color_format = renderer.output_depth_format
        renderer_output_depth_format = renderer.output_depth_format
    
    # 出力画像の読み込み
    color_img = cv2.imread (out_dir+'/temp/color/image0001.png')
    # WEBメルカトルへ変換
    color_web = image_utility.ImageUtility.convert_to_web_mercator(color_img)
    # クリッピング
    color_clipped_img = image_utility.ImageUtility.clip_with_bbox(color_web,clip_center,clip_range)
    cv2.imwrite(out_dir+'/temp/color_web_mercator/image0001.png',color_web)
    cv2.imwrite(out_dir+'/temp/color_web_mercator_clipped/image0001.png',color_clipped_img)
    # 出力画像の読み込み
    depth_img = None
    print(renderer_output_depth_format)
    if renderer_output_depth_format == 'PNG':
        depth_img = cv2.imread (out_dir+'/temp/depth/image0001.png',cv2.IMREAD_UNCHANGED)
    if renderer_output_depth_format == 'HDR':
        depth_img = cv2.imread (out_dir+'/temp/depth/image0001.hdr',cv2.IMREAD_UNCHANGED)
        depth_img_saved = np.clip(depth_img * 255, 0, 255).astype(np.uint8)
        cv2.imwrite (out_dir+'/temp/depth/image0001.png',depth_img_saved)
    
    depth_web = image_utility.ImageUtility.convert_to_web_mercator(depth_img)

    if renderer_output_depth_format == 'PNG':
        cv2.imwrite(out_dir+'/temp/depth_web_mercator/image0001.png',depth_web)
    if renderer_output_depth_format == 'HDR':
        cv2.imwrite(out_dir+'/temp/depth_web_mercator/image0001.hdr',depth_web)
        depth_web_saved = np.clip(depth_img * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(out_dir+'/temp/depth_web_mercator/image0001.png',depth_web_saved)
    
    # WEBメルカトルへ変換
    depth_clipped_img = image_utility.ImageUtility.clip_with_bbox(depth_web,clip_center,clip_range)
    # クリッピング
    if renderer_output_depth_format == 'PNG':
        cv2.imwrite(out_dir+'/temp/depth_web_mercator_clipped/image0001.png',depth_clipped_img)
    if renderer_output_depth_format == 'HDR':
        cv2.imwrite(out_dir+'/temp/depth_web_mercator_clipped/image0001.hdr',depth_clipped_img)
        depth_clipped_img_saved = np.clip(depth_clipped_img * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(out_dir+'/temp/depth_web_mercator_clipped/image0001.png',depth_clipped_img_saved)

    if mode == 'Grid':
        # 離散格子の幅とサイズ
        delta_size = 8
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
        debug_image = gaussian_blur.GaussianBlur.apply_whole_blur2d_from_depth(color_clipped_img,depth_clipped_img,index_image,vis_mode=True)
        # array.map(|x x*2|)
        # 処理を分解してnumpyのお作法に従うように変換するコスト(実装コスト)
        # →今日試せる？
        # 四角形へ変換する
        grid_img = grid_filter.GridFilter.apply_filter(gauss_image,delta_size,delta_size,0.1)
        cv2.imwrite(out_dir+'/result/gauss_output.png',gauss_image) # OK
        cv2.imwrite(out_dir+'/result/debug_output.png',debug_image) # OK
        cv2.imwrite(out_dir+'/result/final_output.png',grid_img) # OK
    if mode == 'Hex':
        # WEBメルカトルへ変換
        hex_filter = hex_filter.HexFilter(size=(512,512), pad_size= (50,50),diam=16,nx=32)
        gauss_image = gaussian_blur.GaussianBlur.apply_whole_blur1d_from_depth(color_clipped_img,depth_clipped_img,hex_filter.hex_indices,9,15,100,vis_mode=False)
        debug_image = gaussian_blur.GaussianBlur.apply_whole_blur1d_from_depth(color_clipped_img,depth_clipped_img,hex_filter.hex_indices,9,15,100,vis_mode=True)
        gauss_image = gauss_image.astype(np.float32)/255.0
        gauss_image = gauss_image[:,[2, 1, 0]]
        debug_image = debug_image.astype(np.float32)/255.0
        debug_image = debug_image[:,[2, 1, 0]]
        hex_filter.render(gauss_image,out_dir+'/result/final_output_hex.png')
        hex_filter.render(debug_image,out_dir+'/result/debug_output_hex.png')

    