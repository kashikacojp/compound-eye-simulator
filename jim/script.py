import bpy
import os

print("Start Blender Setting")

# Parameters
working_path    = 'F:/Work/KASHIKA/Develop/compound-eye-simulator/Flower/jim'
output_color_path = os.path.join(working_path, 'output_color')
output_depth_path = os.path.join(working_path, 'output_depth')
background_image_path = os.path.join(working_path, '../symmetrical_garden_02_4k.hdr')

# Scene path
#scene_path      = os.path.join(working_path, '../flower_middle.blend')
#print(scene_path)
#bpy.ops.wm.open_mainfile(filepath=scene_path)

#
# Rendering Setting
#
bpy.context.scene.render.engine                     = 'CYCLES'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath                   = output_color_path
bpy.context.scene.render.resolution_x               = 4096
bpy.context.scene.render.resolution_y               = 2048
bpy.context.scene.cycles.use_denoising              = True
bpy.context.scene.cycles.device                     = 'GPU'
bpy.context.scene.cycles.samples                    = 10
bpy.context.scene.use_nodes = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True

#
# Set Render Nodes
#
scene_node_tree = bpy.context.scene.node_tree
# clear default nodes
for node in scene_node_tree.nodes:
    scene_node_tree.nodes.remove(node)
node_r_layers = scene_node_tree.nodes.new('CompositorNodeRLayers')
node_r_layers.name = 'render layers'
output_color = None
output_depth = None
for output in node_r_layers.outputs:
    if output.name == 'Image':
        output_color = output
    if output.name == 'Depth':
        output_depth = output
node_norm_depth = scene_node_tree.nodes.new('CompositorNodeNormalize')
node_norm_depth.name = 'norm_depth'
node_save_color = scene_node_tree.nodes.new('CompositorNodeOutputFile')
node_save_color.name = 'save_color'
node_save_color.base_path =  output_color_path
node_save_depth = scene_node_tree.nodes.new('CompositorNodeOutputFile')
node_save_depth.name = 'save_depth'
#if output_depth_format == 'HDR':
#    node_save_depth.format.file_format = "HDR" # default is "PNG"
#    node_save_depth.format.color_mode  = "RGB"  # default is "BW"
#    node_save_depth.format.color_depth = "32"
#    node_save_depth.format.compression = 0     # default is 15
#    node_save_depth.base_path =  output_depth_path
#else:
node_save_depth.base_path =  output_depth_path


scene_node_tree.links.new(output_color,node_save_color.inputs[0])
scene_node_tree.links.new(output_depth,node_norm_depth.inputs[0])
scene_node_tree.links.new(node_norm_depth.outputs[0],node_save_depth.inputs[0])

cycles_preferences = bpy.context.preferences.addons['cycles'].preferences
cycles_preferences.compute_device_type = 'CUDA'
if cycles_preferences.compute_device_type == 'CUDA':
    cycles_preferences.get_devices()
    for device in cycles_preferences.devices:
        if device.type == 'CUDA' and device.name == 'NVIDIA CUDA':
            print("FOUND: CUDA")
            device.use = True
            cycles_preferences.compute_device = device.name
            cycles_preferences.compute_device_type = 'OPTIX'
            break

# 環境マップをロード
image = bpy.data.images.load(background_image_path)

# シーンの設定
scene = bpy.context.scene
world = scene.world
node_background = world.node_tree.nodes['Background']

# Add Environment Texture node
node_environment = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
node_environment.image = image

# Link all nodes
links = world.node_tree.links
link  = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])

# カメラを格納する変数を初期化
camera = None

# シーン内のすべてのオブジェクトを取得
objects = bpy.context.scene.objects

# すべてのオブジェクトをチェックしてカメラを見つける
for obj in objects:
    if obj.type == 'CAMERA':
        camera = obj    
camera.data.type = 'PANO'
camera.data.panorama_type = 'EQUIRECTANGULAR'
camera.data.clip_start = 0.001
camera.data.clip_end   = 10000
scene.camera = camera

# レンダリング実行
bpy.ops.render.render(write_still=True)