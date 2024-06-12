import image_utility
import scene_renderer
import gaussian_blur
import grid_filter
import hex_filter
import numpy as np
import os
import cv2
import sys
import argparse

if __name__ == '__main__':
    # 引数の処理
    parser = argparse.ArgumentParser(description='Generate compound eye image from a scene file')
    parser.add_argument('-s', '--scene'     , type=str             , help='シーンのファイルパス', default='./../Flower/flower.blend')
    parser.add_argument('-i', '--image'     , type=str             , help='環境マップのパス', default='./../symmetrical_garden_02_4k.hdr')
    parser.add_argument('-o', '--output'    , type=str             , help='出力ディレクトリ', default='./../output')
    parser.add_argument('-m', '--mode'      , type=str             , help='モード(現在はHexのみ)', default='Hex')
    parser.add_argument('--skip-render'     , type=bool            , help='描画をスキップして、現在の出力に適用', default=False)
    parser.add_argument('--clip-center'     , type=float, nargs="*", help='極座標系におけるクリップの中心位置([0,0]~[±180,±90])'     , default=[0.0, 0.0])
    parser.add_argument("--ommatidia-fov"   , type=float           , help='個眼の視野角'                  , default=30) 
    parser.add_argument('--ommatidia-delta' , type=float           , help='個眼の間隔(方位角)'             , default=2)
    parser.add_argument('--ommatidia-count' , type=int             , help='個眼の個数(方位角)'             , default=30)
    parser.add_argument('--aspect'          , type=float           , help='アスペクト比'                   , default=1.0)
    parser.add_argument('--max-depth'       , type=float           , help='深度の最大値, デフォルトはクリップ範囲内の最大深度値を使用', default=-1)
    parser.add_argument('--min-depth'       , type=float           , help='深度の最小値, デフォルトはクリップ範囲内の最小深度値を使用', default=-1)
    parser.add_argument('--depth-step'      , type=int             , help='深度の離散ステップ数'            , default=10)
    parser.add_argument('--sigma'           , type=float           , help='ガウシアンフィルタの分散'        , default=9)
    parser.add_argument('--padding'         , type=int             , help='エッジの範囲外防止用のパディング' , default=300)
    args = parser.parse_args()
    # 引数の取得
    scene_filename = args.scene
    image_filename = args.image
    out_dir        = args.output
    mode           = args.mode
    skip_render    = args.skip_render
    clip_center_deg_phi     = args.clip_center[0]
    clip_center_deg_theta   = args.clip_center[1]
    ommatidia_fov           = args.ommatidia_fov
    ommatidia_delta         = args.ommatidia_delta
    ommatidia_count         = args.ommatidia_count
    aspect                  = args.aspect
    min_depth               = args.min_depth
    max_depth               = args.max_depth
    depth_step              = args.depth_step
    filt_sigma              = args.sigma
    padding                 = args.padding

    if min_depth >= max_depth:
        min_depth = None
        max_depth = None
    else:
        if min_depth < 0:
            min_depth = None
        if max_depth < 0:
            max_depth = None

    # ファイルの存在確認
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

    if not os.path.exists(out_dir+'/temp/color_clipped'):
        os.mkdir(out_dir+'/temp/color_clipped')

    if not os.path.exists(out_dir+'/temp/depth_clipped'):
        os.mkdir(out_dir+'/temp/depth_clipped')

    if not os.path.exists(out_dir+'/result'):
        os.mkdir(out_dir+'/result')

    renderer_output_depth_format = 'HDR'

    if not skip_render:
        renderer = scene_renderer.SceneRenderer(
            scene_filename,
            image_filename, 
            output_path=out_dir+'/temp',
            output_color_path=out_dir+'/temp/color',
            output_depth_path=out_dir+'/temp/depth',
            output_depth_format='HDR'
        )
        renderer.run()
        renderer_output_depth_format = renderer.output_depth_format

    # 出力画像の読み込み
    color_img = cv2.imread (out_dir+'/temp/color/image0001.png')
    # クリッピング
    color_clipped_img = image_utility.ImageUtility.clip_with_plate_carree_bbox(color_img, clip_center_deg_phi, clip_center_deg_theta, ommatidia_delta, ommatidia_count, aspect)
    cv2.imwrite(out_dir+'/temp/color/image0001.png',color_img)
    cv2.imwrite(out_dir+'/temp/color_clipped/image0001.png',color_clipped_img)
    # 出力画像の読み込み
    depth_img = None
    print(renderer_output_depth_format)
    if renderer_output_depth_format == 'PNG':
        depth_img = cv2.imread (out_dir+'/temp/depth/image0001.png',cv2.IMREAD_UNCHANGED)
    if renderer_output_depth_format == 'HDR':
        depth_img = cv2.imread (out_dir+'/temp/depth/image0001.hdr',cv2.IMREAD_UNCHANGED)
        depth_img_saved = np.clip(depth_img * 255, 0, 255).astype(np.uint8)
        cv2.imwrite (out_dir+'/temp/depth/image0001.png',depth_img_saved)
    
    # クリッピング
    depth_clipped_img = image_utility.ImageUtility.clip_with_plate_carree_bbox(depth_img, clip_center_deg_phi, clip_center_deg_theta, ommatidia_delta, ommatidia_count, aspect)
    if renderer_output_depth_format == 'PNG':
        cv2.imwrite(out_dir+'/temp/depth_clipped/image0001.png',depth_clipped_img)
    if renderer_output_depth_format == 'HDR':
        cv2.imwrite(out_dir+'/temp/depth_clipped/image0001.hdr',depth_clipped_img)
        depth_clipped_img_saved = np.clip(depth_clipped_img * 255, 0, 255).astype(np.uint8)
        cv2.imwrite(out_dir+'/temp/depth_clipped/image0001.png',depth_clipped_img_saved)

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
        _, width, _ = color_img.shape
        clipped_height, clipped_width, _ = color_clipped_img.shape
        # WEBメルカトルへ変換
        max_filt_size = 2*int((width * ommatidia_fov / 360.0)/2.0/2.0)+1
        print("max_filt_size=",max_filt_size)
        hex_filter  = hex_filter.HexFilter(size=(clipped_width,clipped_height),diam=16,nx=32)
        input_image = hex_filter.sample(color_clipped_img)
        gauss_image = gaussian_blur.GaussianBlur.apply_whole_blur1d_from_depth(color_clipped_img,depth_clipped_img,hex_filter.hex_indices,min_depth,max_depth,None,filt_sigma,max_filt_size,depth_step,padding,vis_mode=False)
        debug_image = gaussian_blur.GaussianBlur.apply_whole_blur1d_from_depth(color_clipped_img,depth_clipped_img,hex_filter.hex_indices,min_depth,max_depth,None,filt_sigma,max_filt_size,depth_step,padding,vis_mode= True)
        # 入力をそのまま出力した場合を出したい
        input_image = input_image.astype(np.float32)/255.0
        input_image = input_image[:,[2, 1, 0]]
        gauss_image = gauss_image.astype(np.float32)/255.0
        gauss_image = gauss_image[:,[2, 1, 0]]
        debug_image = debug_image.astype(np.float32)/255.0
        debug_image = debug_image[:,[2, 1, 0]]
        hex_filter.render(input_image,out_dir+'/result/final_input_hex.png')
        hex_filter.render(gauss_image,out_dir+'/result/final_output_hex.png')
        hex_filter.render(debug_image,out_dir+'/result/debug_output_hex.png')

    