import bpy
import numpy
import cv2
import os
from os.path import abspath
class SceneRenderer:

    scene_path            = None
    image_path            = None
    output_path           = None
    output_color_path     = None
    output_depth_path     = None
    camera_location       = None
    camera_rotation_euler = None
    camera_clip_start     = None
    camera_clip_end       = None
    
    def __init__(self,scene_path = None,image_path= None,output_path= None,output_color_path= None,output_depth_path = None):
        self.scene_path = scene_path
        self.image_path = image_path
        if output_path is None:
            output_path = '.'
        self.output_path = output_path
        if output_color_path is None:
           output_color_path = abspath(output_path + '/../output_color')
        self.output_color_path = abspath(output_color_path)
        if output_depth_path is None:
           output_depth_path = abspath(output_path + '/../output_depth')
        self.output_depth_path = abspath(output_depth_path)
    
    
if __name__ == '__main__':
    renderer = SceneRenderer()
    

