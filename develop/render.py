import os
from step1_calculate_pixel_viewport.code import calculate_pixel_viewport
from step2_batch_eye_rendering.code      import scene_renderer
from step3_apply_hexigonal_filter.code   import apply_hexigonal_filter

settings = {
    "scene_path"           : "D:/Users/shums/kasika/20240703/compound-eye-simulator/assets/flower_middle_compress.blend", 
    "output_width"         : 1920,
    "output_height"        : 1080,
    "image_format"         : "../step1-panorama-rendering/output_color/*.png",
    "interommatidial_angle": 1.5,
    "ommatidium_angle"     : 1.5,
    "ommatidium_count"     : 4,
    "ommatidium_radius"    : 0.00001,
    "theta"                : 0,
    "phi"                  : 0,
    "filter"               : "hexagonal_depth_gaussian",
    "view_mode"            : "depth",
    "debug_mode"           : False,
    "blur_size"            : 60,
    "frame"                : 1
}

basedir = os.path.dirname(os.path.abspath(__file__))
color_image_dir = os.path.join(basedir,"output","temp_color_image")
depth_image_dir = os.path.join(basedir,"output","temp_depth_image")
output_dir = os.path.join(basedir,"output")
print(color_image_dir)
print(output_dir)

hex_pos_setting = calculate_pixel_viewport.run(settings)
scene_path = settings["scene_path"]
frame_index = settings["frame"]
scene_renderer.run(scene_path, hex_pos_setting, color_image_dir,depth_image_dir,frame_index) # Generate Images in output_color/output_depth folder
apply_hexigonal_filter.run(settings,color_image_dir, output_dir,frame_index) # Generate Images in output_color/output_depth folder

