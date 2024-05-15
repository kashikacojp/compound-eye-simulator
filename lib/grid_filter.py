import cv2
import sys
import os
import numpy as np
from os.path import abspath

class GridFilter:
    @staticmethod
    def apply_filter(input_image,size_x,size_y,grid_scale):
        input_height,input_width,input_channel = input_image.shape
        output_image = np.zeros((size_y*input_height,size_x*input_width,input_channel),input_image.dtype)
        height,width,_=output_image.shape
        for y in range(0,height):
            dy = y %size_y
            for x in range(0,width):
                dx = x %size_x
                for c in range(0,input_channel):
                    output_image[y,x,c] = input_image[int(y/size_y),int(x/size_x),c]
                    if (dx < max(size_x * grid_scale,1)):
                        output_image[y,x,c] = 0
                    if (dy < max(size_y * grid_scale,1)):
                        output_image[y,x,c] = 0
                    
        return output_image

if __name__ == '__main__':
    delta_size = 8
    color_img = cv2.imread('./../output_color_web_mercator_clipped/image0001_with_depth.png')
    grid_img = GridFilter.apply_filter(color_img,delta_size,delta_size,0.1)
    cv2.imwrite('./../output_color_web_mercator_clipped/image0001_with_grid.png',grid_img) # OK
    # cv2.imwrite('./../output_color_web_mercator_clipped/Lenna_blur2.png',color_out2) # OK
