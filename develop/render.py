import os

from step1_calculate_pixel_viewport.code import calculate_pixel_viewport
from step2_batch_eye_rendering.code      import scene_renderer
from step3_apply_hexigonal_filter.code   import apply_hexigonal_filter

def show_result_image(path):
    # ここに画像を表示する処理を書く
    
def rander_frame(settings):
    basedir = os.path.dirname(os.path.abspath(__file__))
    color_image_dir = os.path.join(basedir,"output","temp_color_image", "radius"+str(settings["ommatidium_radius"]),"frame"+str(settings["frame"]))
    depth_image_dir = os.path.join(basedir,"output","temp_depth_image", "radius"+str(settings["ommatidium_radius"]),"frame"+str(settings["frame"]))
    output_dir = os.path.join(basedir,"output")
    print(color_image_dir)
    print(output_dir)
    if not os.path.exists(color_image_dir):
        os.makedirs(color_image_dir)
    if not os.path.exists(depth_image_dir):
        os.makedirs(depth_image_dir)
    hex_pos_setting = calculate_pixel_viewport.run(settings)
    scene_path = settings["scene_path"]
    frame_index = settings["frame"]
    scene_renderer.run(scene_path, hex_pos_setting, color_image_dir,depth_image_dir,frame_index) # Generate Images in output_color/output_depth folder
    settings['debug_mode'] = False
    apply_hexigonal_filter.run(settings,color_image_dir, output_dir,frame_index) # Generate Images in output_color/output_depth folder
    settings['debug_mode'] = True
    apply_hexigonal_filter.run(settings,color_image_dir, output_dir,frame_index) # Generate Images in output_color/output_depth folder
    radius = settings["ommatidium_radius"]
    # output_dirにradius=radiusのフォルダを作成
    radius_output_dir = os.path.join(output_dir, "radius="+str(radius), "frame"+str(frame_index))
    # output_dirにある全ての*.pngファイルをradius_output_dirに移動
    os.makedirs(radius_output_dir, exist_ok=True)
    for file in os.listdir(output_dir):
        if file.endswith(".png"):
            os.rename(os.path.join(output_dir, file), os.path.join(radius_output_dir, file))
    
    result_image_path = "" # ここに結果の画像のパスを入れる
    show_result_image(result_image_path)

def render_animation(settings):
    # total_frame = 600
    # frames            = range(1, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)
    
    # frames            = range(2, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)

    # frames            = range(3, total_frame + 1, 3) 
    # for frame in frames:
    #     settings["frame"] = frame
    #     rander_frame(settings)
    rander_frame(settings)

# setting
settings = {
    "scene_path"           : "E:/yaikeda/Project/20240625_compound-eye-simulator/scene/purple/20240726/flower_middle.blend", 
    "output_width"         : 1920,
    "output_height"        : 1080,
    "image_format"         : "../step1-panorama-rendering/output_color/*.png",
    "interommatidial_angle": 1.5,
    "ommatidium_angle"     : 1.5,
    "ommatidium_count"     : 25,
    "ommatidium_radius"    : 0.0,
    "theta"                : 0,
    "phi"                  : 0,
    "filter"               : "hexagonal_depth_gaussian",
    "view_mode"            : "color",
    "debug_mode"           : True,
    "blur_size"            : 90,
    "frame"                : 275
}
render_animation(settings)
