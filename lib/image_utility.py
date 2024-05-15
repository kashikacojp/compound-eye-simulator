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

# if __name__ == '__main__':
#     color_img = cv2.imread("./../output_color/image0001.png")
#     color_web = ImageUtility.convert_to_web_mercator(color_img)
#     cv2.imwrite('./../output_color_web_mercator/image0001.png',color_web) # OK
#     color_img_clipped = ImageUtility.clip_with_bbox(color_web,(0,0),(1024,1024))
#     cv2.imwrite('./../output_color_web_mercator/image0001_clipped.png',color_img_clipped)
#     depth_img = cv2.imread("./../output_depth/image0001.png")
#     depth_web = ImageUtility.convert_to_web_mercator(depth_img)
#     cv2.imwrite('./../output_depth_web_mercator/image0001.png',depth_web)
#     depth_img_clipped = ImageUtility.clip_with_bbox(depth_web,(0,0),(1024,1024))
#     cv2.imwrite('./../output_depth_web_mercator/image0001_clipped.png',depth_img_clipped)

