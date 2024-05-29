import cv2
import sys
import os
import numpy as np
from   os.path import abspath
from   hexalattice.hexalattice import *
import numpy as np
from matplotlib import pyplot as plt

class HexFilter:
    x_size     = 256
    y_size     = 256
    x_range    = 506
    y_range    = 506
    nx         = 1
    ny         = 1
    bound_min  = None
    bound_max  = None
    diam       = 64
    hex_centers= None
    hex_indices= None
    # TODO: 画像のクリップ範囲に対して、格子のX方向の六角形数が与えられたとき、Y方向の六角形数および直径を計算できるようにする
    def __init__(self,size = (256,256), pad_size= (50,50), diam=64):
        x_size,y_size = size
        x_pad_size,y_pad_size = pad_size
        x_range = x_size + x_pad_size * 2
        y_range = y_size + y_pad_size * 2
        nx =np.ceil((x_range/(diam * np.sqrt(3.0)/2.0))-0.5)
        ny =np.ceil((y_range/diam-1)*(4.0/3.0))
        print("nx="+str(nx)+", ny="+str(ny))
        hex_centers, _ = create_hex_grid(nx=nx,ny=ny,min_diam=diam,do_plot=False)
        max_x = np.max(hex_centers[:, 0]) 
        max_y = np.max(hex_centers[:, 1])
        min_x = np.min(hex_centers[:, 0]) 
        min_y = np.min(hex_centers[:, 1])
        cen_x =(max_x+min_x)/2
        cen_y =(max_y+min_y)/2
        # print("["+str(min_x)+","+str(max_x)+"]x["+str(min_y)+","+str(max_y)+"]")
        bound_min_x = cen_x - x_size/2
        bound_max_x = cen_x + x_size/2
        bound_min_y = cen_y - y_size/2
        bound_max_y = cen_y + y_size/2
        print("["+str(bound_min_x)+","+str(bound_max_x)+"]x["+str(bound_min_y)+","+str(bound_max_y)+"]")
        hex_indices = hex_centers.copy()
        hex_indices[:,0] = np.round(hex_indices[:,0] - bound_min_x)
        hex_indices[:,1] = np.round(bound_max_y - hex_indices[:,1])
        hex_indices = hex_indices.astype(np.int32)
        # print(hex_indices)

        self.x_size = x_size
        self.y_size = y_size
        self.x_range = x_range
        self.y_range = y_range
        self.nx = nx
        self.ny = ny
        self.diam = diam
        self.hex_centers = hex_centers
        self.hex_indices = hex_indices
        self.bound_min = (bound_min_x,bound_min_y)
        self.bound_max = (bound_max_x,bound_max_y)
    def render(self,color_web,filename = None):
        x_hex_coords = self.hex_centers[:, 0]
        y_hex_coords = self.hex_centers[:, 1]
        h_fig = plt.figure(figsize=(self.x_size/16, self.y_size/16))
        h_ax = h_fig.add_axes([0, 0, 1, 1])
        ax = plot_single_lattice_custom_colors(x_hex_coords, y_hex_coords,
                                    face_color  = color_web,
                                    edge_color  = color_web,
                                    min_diam    = self.diam*0.99,
                                    h_ax        = h_ax,
                                    plotting_gap= 0.05,
                                    rotate_deg  = 0)
        (bound_min_x,bound_min_y) = self.bound_min
        (bound_max_x,bound_max_y) = self.bound_max
        # print(ax)      
        # print(hex_centers)                     
        ax.axis("off")
        ax.axis('tight')
        ax.set_xlim(bound_min_x,bound_max_x)       
        ax.set_ylim(bound_min_y,bound_max_y) 
        # plt.margins(x=0,y=0)
        if not filename:
            h_fig.show()
        else :
            h_fig.savefig(filename,bbox_inches='tight',pad_inches=0,dpi=16)

# import gaussian_blur
# if __name__ == "__main__":
#     hex_filter = HexFilter(size=(460,460), pad_size= (10,10),diam=8)
#     color_clipped_img = cv2.imread("./../output_color_web_mercator_clipped/image0001.png")
#     depth_clipped_img = cv2.imread("./../output_depth_web_mercator_clipped/image0001.png")
#     # WEBメルカトルへ変換
#     color_web = gaussian_blur.GaussianBlur.apply_whole_blur1d_from_depth(color_clipped_img,depth_clipped_img,hex_filter.hex_indices)
#     color_web = color_web.astype(np.float32)/255.0
#     color_web = color_web[:,[2, 1, 0]]
#     x_hex_coords = hex_filter.hex_centers[:, 0]
#     y_hex_coords = hex_filter.hex_centers[:, 1]
#     ax = plot_single_lattice_custom_colors(x_hex_coords, y_hex_coords,
#                                   face_color  =color_web,
#                                   edge_color  =color_web,
#                                   min_diam    =hex_filter.diam*0.99,
#                                   plotting_gap=0.05,
#                                   rotate_deg  =0)
#     (bound_min_x,bound_min_y) = hex_filter.bound_min
#     (bound_max_x,bound_max_y) = hex_filter.bound_max
#     # print(ax)      
#     # print(hex_centers)                     
#     ax.axis("off")
#     plt.xlim(bound_min_x,bound_max_x)       
#     plt.ylim(bound_min_y,bound_max_y) 
#     plt.show()


