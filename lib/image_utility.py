import cv2
import sys
import os
import numpy as np
from os.path import abspath

class ImageUtility:
    @staticmethod
    def convert_to_web_mercator(image):
        # 同じサイズの空の画像を作成
        height, width, channels = image.shape
        output_image = np.zeros((width, width, channels), dtype=image.dtype)

        lon = (+0.9450125419978511*0.5) * np.pi# デフォルトだと赤道が0.5になるので, -0.5を引く
        # print(np.log(np.tan(lon/2+np.pi/4)))# -2.13
        # 画素値をコピー
        for y in range(width):
            # width/2を引くと[-width/2 ~ width/2]になる
            # height=width/2より, [-1 ~ 1]になる
            # [-2 ~ 2]にしたいので2倍する
            lon = np.pi*((float(y) - width/2)/float(height))
            paranoma_lon = np.arcsin(np.tanh(lon))# [-pi/2 ~ pi/2]
            # print(paranoma_lon)
            if paranoma_lon == float('inf'):
                continue
            if paranoma_lon == float('-inf'):
                continue
            paranoma_y = int(height * (paranoma_lon + np.pi/2) / np.pi) # [0 ~ height]
            if (paranoma_y < 0) or (paranoma_y >= width):
                continue

            for x in range(width):
                output_image[y, x] = image[paranoma_y, x]
            
        return output_image
    @staticmethod
    def convert_to_plate_carree(image):
        # 同じサイズの空の画像を作成
        height, width, channels = image.shape
        height = int(width/2)
        output_image = np.zeros((height, width, channels), dtype=image.dtype)

        # 画素値をコピー
        for y in range(width):
            # width/2を引くと[-width/2 ~ width/2]になる
            # height=width/2より, [-1 ~ 1]になる
            # [-2 ~ 2]にしたいので2倍する
            lon = np.pi*((float(y) - width/2)/float(height))
            paranoma_lon = np.arcsin(np.tanh(lon))# [-pi/2 ~ pi/2]
            # print(paranoma_lon)
            if paranoma_lon == float('inf'):
                continue
            if paranoma_lon == float('-inf'):
                continue
            paranoma_y = int(height * (paranoma_lon + np.pi/2) / np.pi) # [0 ~ height]
            if (paranoma_y < 0) or (paranoma_y >= width):
                continue

            for x in range(width):
                output_image[paranoma_y, x] = image[y, x]
        
        return output_image
    @staticmethod
    def clip_with_bbox(image, clip_center, clip_range):
        height, width, channels = image.shape
        center_x,center_y = clip_center
        range_x ,range_y  = clip_range
        clipped_image = np.zeros((range_y, range_x, channels), dtype=image.dtype)
        print("channels=",channels)
        for y in range(range_y):
            ry = int(y+height/2+center_y-range_y/2)
            if ry < 0 or ry >= height:
                continue
            for x in range(range_x):
                rx = int(x+width/2+center_x-range_x/2)
                if rx < 0 or rx >= width:
                    continue
                clipped_image[y,x] = image[ry,rx]
        return clipped_image
    @staticmethod
    def clip_with_plate_carree_bbox(image, clip_center_deg_phi,  clip_center_deg_theta, ommatidia_delta_deg_phi, ommatidia_count, aspect = 1.0):
        # 正距円筒図法としてクリッピング
        # ommatidia_delta_deg: 個眼間の角度
        # ommatidia_count: 個眼の数
        # clip_with_bboxを内部的に使う
        # 最終的な画像の縦横比をaspectで指定
        height, width, channels = image.shape
        clip_center = (int( (clip_center_deg_phi)*width/360.0), int( (clip_center_deg_theta)*height/180.0))
        clip_range_x= int(ommatidia_count*ommatidia_delta_deg_phi*width/360.0)
        clip_range_y= int(clip_range_x * aspect)
        clip_range  = (clip_range_x, clip_range_y)
        print("clip_center=",clip_center)
        print("clip_range=",clip_range)
        return ImageUtility.clip_with_bbox(image, clip_center, clip_range)