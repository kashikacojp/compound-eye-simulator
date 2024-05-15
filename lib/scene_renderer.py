import bpy
import numpy
import cv2
import sys
import os
from os.path import abspath

class SceneRenderer:
    scene_path            = None
    background_image_path = None
    output_path           = None
    output_color_path     = None
    output_depth_path     = None

    def __init__(self, scene_path = None,background_image_path= None,output_path= None,output_color_path= None,output_depth_path = None):
        if scene_path is not None:
            self.load_scene(scene_path)
        
        self.background_image_path = abspath(background_image_path)
        if output_path is None:
            output_path = '.'
        self.output_path = abspath(output_path)
        if output_color_path is None:
           output_color_path = abspath(output_path + '/../output_color')
        self.output_color_path = abspath(output_color_path)
        if output_depth_path is None:
           output_depth_path = abspath(output_path + '/../output_depth')
        self.output_depth_path = abspath(output_depth_path)
    def load_scene(self, scene_path):
        if (scene_path is None):
            return False
        scene_path = abspath(scene_path)
        try :
            bpy.ops.wm.open_mainfile(filepath=scene_path)
        except:
            return False
        self.scene_path = scene_path
        return True 
    def run(self):
        #  シーンの読み込み
        bpy.ops.wm.open_mainfile(filepath=self.scene_path)
        # レンダリング設定
        bpy.context.scene.render.engine                     = 'CYCLES'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        #bpy.context.scene.render.image_settings.use_preview = False
        bpy.context.scene.render.filepath                   = self.output_path
        bpy.context.scene.render.resolution_x               = 4096
        bpy.context.scene.render.resolution_y               = 2048
        bpy.context.scene.cycles.use_denoising              = True
        bpy.context.scene.cycles.device                     = 'GPU'
        bpy.context.scene.cycles.samples                    = 10
        bpy.context.scene.use_nodes = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True
        scene_node_tree = bpy.context.scene.node_tree
        # clear default nodes
        for node in scene_node_tree.nodes:
            scene_node_tree.nodes.remove(node)

        node_r_layers = scene_node_tree.nodes.new('CompositorNodeRLayers')
        node_r_layers.name = 'render layers'
        print('location'+str(node_r_layers.location)) 
        print('scene'+str(node_r_layers.scene)) 
        output_color = None
        output_depth = None

        for output in node_r_layers.outputs:
            if output.name == 'Image':
                output_color = output
            if output.name == 'Depth':
                output_depth = output
            
        if output_color:
            print("output_color found:", output_color.name)
        else:
            print("No output_color found in the render layer.")
                
        if output_depth:
            print("output_depth found:", output_depth.name)
        else:
            print("No output_depth found in the render layer.")
            
        node_norm_depth = scene_node_tree.nodes.new('CompositorNodeNormalize')
        node_norm_depth.name = 'norm_depth'
        node_save_color = scene_node_tree.nodes.new('CompositorNodeOutputFile')
        node_save_color.name = 'save_color'
        node_save_color.base_path =  self.output_color_path
        node_save_depth = scene_node_tree.nodes.new('CompositorNodeOutputFile')
        node_save_depth.name = 'save_depth'
        node_save_depth.base_path =  self.output_depth_path
        node_save_depth.format.file_format = "HDR" # default is "PNG"
        node_save_depth.format.color_mode  = "RGB"  # default is "BW"
        node_save_depth.format.color_depth = "32"
        node_save_depth.format.compression = 0     # default is 15

        scene_node_tree.links.new(output_color,node_save_color.inputs[0])
        scene_node_tree.links.new(output_depth,node_norm_depth.inputs[0])
        scene_node_tree.links.new(node_norm_depth.outputs[0],node_save_depth.inputs[0])

        cycles_preferences = bpy.context.preferences.addons['cycles'].preferences
        # デバイスタイプをGPUに設定
        cycles_preferences.compute_device_type = 'CUDA'

        # CUDAデバイスタイプを選択している場合は、OptiXを有効にする
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
        image = bpy.data.images.load(self.background_image_path)

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

        # カメラが見つかった場合は、それを使用する
        if camera:
            print("Camera found:", camera.name)
        else:
            print("No camera found in the scene.")
            
        camera.data.type = 'PANO'
        # camera.location  = camera_location # Cameraの位置を変更する
        # camera.rotation_euler = camera_rotation_euler # Cameraの傾きを変更する
        camera.data.clip_start = 0.001
        camera.data.clip_end   = 10000

        scene.camera = camera
        # レンダリング実行
        bpy.ops.render.render(write_still=True)
    def print(self):
        print("scene_path=",self.scene_path)
        print("output_path=",self.output_path)
        print("output_color_path=",self.output_color_path)
        print("output_depth_path=",self.output_depth_path)

