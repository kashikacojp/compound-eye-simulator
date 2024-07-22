import bpy
import os
from os.path import abspath
import math
from mathutils import Vector, Quaternion, Euler
class SceneRenderer:
    scene_path            = None
    background_image_path = None
    output_depth_format   = None
    output_path           = None
    output_color_path     = None
    output_depth_path     = None
    input_settings        = None
    def __init__(self, input_settings = None, scene_path = None,background_image_path= None,output_path= None,output_color_path= None,output_depth_path = None,output_depth_format = 'PNG'):
        if scene_path is not None:
            self.load_scene(scene_path)
        else:
            print ("scene_path is None")
            scene_path = bpy.data.filepath
            self.scene_path = scene_path
        if background_image_path is None:
            current_file_path = bpy.data.filepath
            current_parent_dir = os.path.dirname(current_file_path)
            # hdrファイルを探す
            for file in os.listdir(current_parent_dir):
                if file.endswith(".hdr"):
                    background_image_path = current_parent_dir + '/' + file
                    break
        self.input_settings = input_settings
        self.background_image_path = abspath(background_image_path)
        if output_path is None:
            current_file_path = bpy.data.filepath
            current_parent_dir = os.path.dirname(current_file_path)
            output_path = current_parent_dir
        self.output_path = abspath(output_path)
        if output_color_path is None:
           output_color_path = abspath(output_path + '/../develop/step2-batch-eye-rendering/output_color')
           if not os.path.exists(output_color_path):
                os.makedirs(output_color_path)
        self.output_color_path = abspath(output_color_path)
        if output_depth_path is None:
           output_depth_path = abspath(output_path + '/../develop/step2-batch-eye-rendering/output_depth')
           if not os.path.exists(output_depth_path):
                os.makedirs(output_depth_path)
        self.output_depth_path = abspath(output_depth_path)
        self.output_depth_format = output_depth_format
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
    def render_image(self, camera, width = 100, height = 100,samples = 10,base_file_name = 'image'):
        # レンダリング設定
        bpy.context.scene.render.engine                     = 'CYCLES'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        #bpy.context.scene.render.image_settings.use_preview = False
        bpy.context.scene.render.filepath                   = self.output_path + '/image.png'
        bpy.context.scene.render.resolution_x               = width
        bpy.context.scene.render.resolution_y               = height
        bpy.context.scene.cycles.samples                    = samples
        bpy.context.scene.cycles.use_denoising              = True
        bpy.context.scene.cycles.device                     = 'GPU'
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
            
        node_save_color = scene_node_tree.nodes.new('CompositorNodeOutputFile')
        node_save_color.name = 'save_color'
        node_save_color.base_path =  self.output_color_path
        node_save_color.file_slots.clear()  # 既存のスロットをクリア
        node_save_color.file_slots.new('MyOutputImage')  # 新しいスロットを追加
        node_save_color.file_slots[0].path  = base_file_name + '_' 
        node_save_depth = scene_node_tree.nodes.new('CompositorNodeOutputFile')
        node_save_depth.name = 'save_depth'
        node_save_depth.base_path =  self.output_depth_path
        node_save_depth.file_slots.clear()  # 既存のスロットをクリア
        node_save_depth.file_slots.new('MyOutputImage')  # 新しいスロットを追加
        node_save_depth.file_slots[0].path = base_file_name + '_'
        if self.output_depth_format == 'OPEN_EXR':
            node_save_depth.format.file_format = "OPEN_EXR" # default is "PNG"
            node_save_depth.format.color_mode  = "RGB"  # default is "BW"
            node_save_depth.format.color_depth = "32"
            node_save_depth.format.compression = 0     # default is 15
        else:
            node_save_depth.format.file_format = "PNG"
            node_save_depth.format.color_mode  = "BW"
            node_save_depth.format.color_depth = "16"
            node_save_depth.format.compression = 0


        scene_node_tree.links.new(output_color,node_save_color.inputs[0])
        scene_node_tree.links.new(output_depth,node_save_depth.inputs[0])

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
        # カメラの設定
        scene.camera = camera
        # レンダリング実行
        bpy.ops.render.render(write_still=True)

    def rotate_camera(self, camera, base_location,base_radius, base_rotation,phi, theta):
        # base_locationは, カメラの位置を球面上に配置するための中心座標
        # base_radius  は, カメラの位置を球面上に配置するための半径
        # base_rotationは, カメラの姿勢を決定するための基準となる回転
        # phi, thetaはそれぞれ極座標系におけるカメラの位置と姿勢を決定するための角度
        # camera座標系におけるlocalな各軸を取得
        local_x_axis = Vector((1, 0, 0))
        local_y_axis = Vector((0, 1, 0))
        local_z_axis = Vector((0, 0,-1))
        # phiの回転を適用
        # 回転軸はlocal_y_axis
        # 回転角はphi
        rotation_matrix = Quaternion(local_y_axis, -phi).to_matrix().to_4x4()
        # thetaの回転を適用
        # 回転軸はlocal_x_axis
        # 回転角はtheta
        rotation_matrix = Quaternion(local_x_axis, -theta).to_matrix().to_4x4() @ rotation_matrix

        # カメラの姿勢として設定
        camera.matrix_world =  camera.matrix_world @ rotation_matrix
        camera.location     = camera_location

    def run(self):
        width = 100
        height = 100
        samples = 10
        base_file_name = 'image'
        # カメラを格納する変数を初期化
        base_camera = None
        # シーン内のすべてのオブジェクトを取得
        objects = bpy.context.scene.objects
        # すべてのオブジェクトをチェックしてカメラを見つける
        for obj in objects:
            if obj.type == 'CAMERA':
                base_camera = obj

        # カメラが見つかった場合は、それを基準とする
        if base_camera:
            print("Camera found:", base_camera.name)
        else:
            print("No camera found in the scene.")
        
        # 個眼間角度を取得(度数)→ラジアンに変換して視野角へ
        ommatidium_angle = self.input_settings['ommatidium_angle']
        camera_field_of_view = ommatidium_angle * 3.141592653589793 / 180.0
        # ベースカメラの位置を取得
        camera_location = base_camera.location
        # ベースカメラの姿勢を取得
        camera_rotation = base_camera.rotation_euler
        # カメラのクリッピング範囲を指定
        if self.input_settings is None:
            print ("input_settings is None")
            return
        if 'centers' not in self.input_settings:
            print ("centers not found in input_settings")
            return
        radius = 1.0
        num_centers = len(self.input_settings['centers'])
        i = 0
        for center in self.input_settings['centers']:
            # 見つかったカメラを複製する
            camera = base_camera.copy()
            camera.data = base_camera.data.copy()
            camera.name = base_camera.name + '_center_' + str(i)
            # 複製したカメラオブジェクトを現在のシーンにリンク
            bpy.context.collection.objects.link(camera)
            camera.data.clip_start = 0.001
            camera.data.clip_end   = 10000
            camera.data.angle = camera_field_of_view
            # 中心角を取得(phiは0~360, thetaは0~180)
            (center_phi, center_theta) = center
            # ラジアンへ変換
            center_phi = center_phi * 3.141592653589793 / 180.0
            center_theta = center_theta * 3.141592653589793 / 180.0
            self.rotate_camera (camera, camera_location, radius, camera_rotation, center_phi, center_theta)
            # 出力ファイル名は, image_${i}.png
            # iは0から始まり, 4桁になるように0埋め
            filename = base_file_name + '_' +  str(i).zfill(4)
            # レンダリング実行
            self.render_image(camera, width, height, samples, filename)
            i = i+1

        # # 複製したカメラを削除する
        # bpy.data.objects.remove(camera)

    def print(self):
        print("scene_path=",self.scene_path)
        print("output_path=",self.output_path)
        print("output_color_path=",self.output_color_path)
        print("output_depth_path=",self.output_depth_path)

if __name__ == "__main__":
    input_settings = {
    'centers': [(-6.0, -3.375), (-4.5, -3.375), (-3.0, -3.375), (-1.5, -3.375), (0.0, -3.375), (1.5, -3.375), (3.0, -3.375), (4.5, -3.375), (-5.25, -2.08125), (-3.75, -2.08125), (-2.25, -2.08125), (-0.75, -2.08125), (0.75, -2.08125), (2.25, -2.08125), (3.75, -2.08125), (5.25, -2.08125), (-6.0, -0.78125), (-4.5, -0.78125), (-3.0, -0.78125), (-1.5, -0.78125), (0.0, -0.78125), (1.5, -0.78125), (3.0, -0.78125), (4.5, -0.78125), (-5.25, 0.51875), (-3.75, 0.51875), (-2.25, 0.51875), (-0.75, 0.51875), (0.75, 0.51875), (2.25, 0.51875), (3.75, 0.51875), (5.25, 0.51875), (-6.0, 1.81875), (-4.5, 1.81875), (-3.0, 1.81875), (-1.5, 1.81875), (0.0, 1.81875), (1.5, 1.81875), (3.0, 1.81875), (4.5, 1.81875), (-5.25, 3.11875), (-3.75, 3.11875), (-2.25, 3.11875), (-0.75, 3.11875), (0.75, 3.11875), (2.25, 3.11875), (3.75, 3.11875), (5.25, 3.11875)],
    'theta': 0,
    'phi': 0,
    'ommatidium_angle': 1.5,
}

    renderer = SceneRenderer(output_depth_format='OPEN_EXR', input_settings=input_settings)
    renderer.print()
    renderer.run()