import cv2
import sys
import os
import numpy as np
from os.path import abspath

class GaussianBlur:
    @staticmethod
    def blur2d_local(image, pixel_x, pixel_y, var, filt_range):
        height, width, _ = image.shape
        accum_pixel  = None
        accum_weight = None
        for y in range(-filt_range,filt_range):
            ry = pixel_y +y
            for x in range(-filt_range,filt_range):
                rx = pixel_x +x
                radius = np.sqrt(x*x+y*y)
                if ry < 0 or ry >= height:
                    continue
                if rx < 0 or rx >= width:
                    continue
                if radius >= filt_range:
                    continue
                weight = np.exp(-((radius*radius)/(2.0*var*var)))
                pixel  = image[ry,rx]
                if accum_pixel is None:
                    accum_pixel = pixel*weight
                    accum_weight= weight
                else:
                    accum_pixel = accum_pixel + pixel*weight
                    accum_weight= accum_weight+weight
        if accum_pixel is None: 
            return None
        
        return accum_pixel/accum_weight
    
    @staticmethod
    def blur2d_whole(image, var, filt_range):
        height, width, channels = image.shape
        output_image = np.zeros((height, width, channels), dtype=np.uint8)
        for y in range(0,height):
            for x in range(0,width):
                pixel =GaussianBlur.blur2d_local(image,x,y,var,filt_range)
                if pixel is not None:
                    output_image[y,x] = pixel

        return output_image


if __name__ == '__main__':
    color_img = cv2.imread("./../output_color_web_mercator_clipped/image0001.png")
    color_web = GaussianBlur.blur2d_whole(color_img,0.001,1)
    cv2.imwrite('./../output_color_web_mercator_clipped/image0001_with_blur.png',color_web) # OK

