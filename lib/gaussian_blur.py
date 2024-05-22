import cv2
import sys
import os
import numpy as np
from os.path import abspath

class GaussianBlur:
    @staticmethod
    def generate_blur2d_kernel(sigma,filter_size):
        m = filter_size
        n = filter_size
        m_half = m // 2
        n_half = n // 2
        weight_sum = 0
        gaussian_filter = np.zeros((m, n), np.float32)
        for y in range(-m_half,m_half):
            for x in range(-n_half,n_half):
                normal = 1 / (2.0 * np.pi * sigma**2.0)
                exp_term = np.exp(-(x**2.0 + y**2.0) / (2.0 * sigma**2.0))
                len = np.sqrt(x*x+y*y)
                if (len > filter_size): 
                    continue
                weight_sum = weight_sum + normal * exp_term
                gaussian_filter[y+m_half, x+n_half] = normal * exp_term

        gaussian_filter[:] = gaussian_filter[:]/weight_sum
        return gaussian_filter

    @staticmethod
    def apply_local_blur2d_kernel(image, pixel_x, pixel_y, filter_size, kernel):
        height,width,channel = image.shape
        output = np.ndarray(channel,dtype=image.dtype)
        filter_range = filter_size // 2
        for c in range(channel):
            sub_img = image[pixel_y-filter_range:pixel_y+filter_range+1,pixel_x-filter_range:pixel_x+filter_range+1,c]
            (t_w,t_h) = sub_img.shape
            # if (t_w!=filter_size or t_h !=filter_size):
            #     print("bug:",pixel_x, pixel_y)
            #     continue
            # else:
            #      print("ok:",pixel_x, pixel_y)
            output[c] = np.sum(sub_img*kernel)
        return output
        
    @staticmethod
    def apply_whole_blur2d_kernel(image, filter_size, kernel,pad):
        height, width, channels = image.shape
        image_pad = np.pad(image,[(pad,pad),(pad,pad),(0,0)],'edge')
        output_image = np.zeros((height, width, channels), dtype=image.dtype)
        for y in range(0,height):
            for x in range(0,width):
                output_image[y,x] = GaussianBlur.apply_local_blur2d_kernel(image_pad,x+pad,y+pad,filter_size,kernel)
        return output_image

    @staticmethod
    def apply_whole_blur2d_from_depth(color_image, depth_image, index_image = None, vis_mode = False):
        pad =100
        # TODO: 事前に計算するのではなくて、連続的に処理するべきか？
        filt_sigma = 1
        filt_size1 = 5
        filt_size2 = 9
        filt_size3 = 13
        filt_size4 = 17
        threshold1 = 0.25
        threshold2 = 0.50
        threshold3 = 0.75
        threshold4 = 1.00
        # TODO: sigmaを固定値にして, filter_sizeのみ変える
        color_ker1 = GaussianBlur.generate_blur2d_kernel(filt_sigma , filt_size1)
        color_ker2 = GaussianBlur.generate_blur2d_kernel(filt_sigma , filt_size2)
        color_ker3 = GaussianBlur.generate_blur2d_kernel(filt_sigma , filt_size3)
        color_ker4 = GaussianBlur.generate_blur2d_kernel(filt_sigma , filt_size4)

        if index_image is None:
            height, width,cha   = color_image.shape
            index_image = np.zeros(( height, width, 2), dtype=np.int32)
            for y in range(0,height):
                for x in range(0,width):
                    index_image[y,x,0] = x
                    index_image[y,x,1] = y
        
        depth_min = np.min(depth_image)# 5
        depth_max = np.max(depth_image)# 154
        print(depth_min,depth_max)
        color_image_pad = np.pad(color_image,[(pad,pad),(pad,pad),(0,0)],'edge')
        _, _,channles   = color_image_pad.shape
        height, width,_ = index_image.shape
        output_image    = np.zeros((height, width, channles), dtype=color_image_pad.dtype)
        for y in range(0,height):
            for x in range(0,width):
                px = index_image[y,x,0]
                py = index_image[y,x,1]
                depth = (depth_image[py,px,0]-depth_min)/(depth_max-depth_min)
                if vis_mode:
                    if depth < threshold1:
                        output_image[y,x] = (255.0*threshold1,255.0*threshold1,255.0*threshold1)
                    elif depth < threshold2:
                        output_image[y,x] = (255.0*threshold2,255.0*threshold2,255.0*threshold2)
                    elif depth < threshold3:
                        output_image[y,x] = (255.0*threshold3,255.0*threshold3,255.0*threshold3)
                    else:
                        output_image[y,x] = (255.0*threshold4,255.0*threshold4,255.0*threshold4)
                else:
                    if depth < threshold1:
                        output_image[y,x] = GaussianBlur.apply_local_blur2d_kernel(color_image_pad,px+pad,py+pad,filt_size1,color_ker1)
                    elif depth < threshold2:
                        output_image[y,x] = GaussianBlur.apply_local_blur2d_kernel(color_image_pad,px+pad,py+pad,filt_size2,color_ker2)
                    elif depth < threshold3:
                        output_image[y,x] = GaussianBlur.apply_local_blur2d_kernel(color_image_pad,px+pad,py+pad,filt_size3,color_ker3)
                    else:
                        output_image[y,x] = GaussianBlur.apply_local_blur2d_kernel(color_image_pad,px+pad,py+pad,filt_size4,color_ker4)
                
        return output_image





if __name__ == '__main__':
    delta_size = 8
    depth_img = cv2.imread("./../output_depth_web_mercator_clipped/image0001.hdr") 
    color_img = cv2.imread("./../output_color_web_mercator_clipped/image0001.png")
    height, width,cha   = color_img.shape
    # IndexMap: 二次元のブラー入力画素値のリクエストを作成
    # 現在は、格子のため、出力そのままのリサイズ～出力画像
    index_image = np.zeros(( int(height/delta_size), int(width/delta_size), 2), dtype=np.int32)
    for y in range(0,int(height/delta_size)):
        for x in range(0,int(width/delta_size)):
            index_image[y,x,0] = min(int(x*delta_size),width)
            index_image[y,x,1] = min(int(y*delta_size),height)
    color_out1 = GaussianBlur.apply_whole_blur2d_from_depth(color_img,depth_img,index_image,True)
    height, width,cha = color_out1.shape
    print(height, width,cha)
    # color_out1 = cv2.resize(color_out1,None,fx=delta_size,fy=delta_size)
    # color_img  = cv2.imread("./../output_color_web_mercator_clipped/Lenna.png")
    # color_out1 = GaussianBlur.apply_whole_blur2d_kernel(color_img,25,color_ker1,25)
    # color_out2 = GaussianBlur.apply_whole_blur2d_kernel(color_img,25,color_ker2,25)
    # # color_img = cv2.imread("./../output_color_web_mercator_clipped/image0001.png")
    # # color_web = GaussianBlur.blur2d_whole(color_img,0.001,2)
    cv2.imwrite('./../output/image0001_with_debug.png',color_out1) # OK
    # cv2.imwrite('./../output_color_web_mercator_clipped/Lenna_blur2.png',color_out2) # OK
