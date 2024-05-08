import bpy
import os
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
bpy.ops.render.render()
bpy.data.images['Render Result'].save_render(filepath=os.path.join(output_dir, 'image.png'))
print("フォルダ内にimage.pngが保存されていれば成功です")