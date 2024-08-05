import os
from step1_calculate_pixel_viewport.code import calculate_pixel_viewport
from step2_batch_eye_rendering.code import scene_renderer
from step3_apply_hexigonal_filter.code import apply_hexigonal_filter

settings = {
    "output_width":1920,
    "output_height": 1080,
    "image_format": "../step1-panorama-rendering/output_color/*.png",
    "interommatidial_angle": 1.5,
    "ommatidium_angle": 1.5,
    "ommatidium_count": 25,
    "theta": 0,
    "phi": 0,
    "filter": "hexagonal_depth_gaussian",
    "view_mode": "color",
    "debug_mode": False,
    "blur_size": 60,
    "frame": 0
}

basedir = os.path.dirname(os.path.abspath(__file__))
color_image_dir = os.path.join(basedir,"output","temp_color_image")
output_dir = os.path.join(basedir,"output")
print(color_image_dir)
print(output_dir)

hex_pos_setting = calculate_pixel_viewport.run(settings)
scene_renderer.run(hex_pos_setting, color_image_dir) # Generate Images in output_color/output_depth folder
apply_hexigonal_filter.run(settings, output_dir) # Generate Images in output_color/output_depth folder
