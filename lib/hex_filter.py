import cv2
import sys
import os
import numpy as np
from os.path import abspath
from thirdparty import hexalattice as hl
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
    def __init__(self, size = (256,256), diam=64,nx=None,ny=None):
        
        x_size,y_size = size
        x_range = x_size
        y_range = y_size
        
        if (nx is None) and (ny is None):
            nx =int(np.ceil((x_range/(diam * np.sqrt(3.0)/2.0))-0.5))
            ny =int(np.ceil((y_range/diam-1)*(4.0/3.0)))
        elif (nx is None):
            diam = y_range / ( (ny * 3.0/4.0)+1)
            nx   = int(np.ceil((x_range/(diam * np.sqrt(3.0)/2.0))-0.5))
        elif (ny is None):
            diam = x_range/((nx+0.5)*np.sqrt(3.0)/2.0)
            ny   =int(np.ceil((y_range/diam-1)*(4.0/3.0)) )
        
        print("nx="+str(nx)+", ny="+str(ny))
        hex_centers, _ = hl.create_hex_grid(nx=nx,ny=ny,min_diam=diam,do_plot=False)
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
        hex_indices = hex_centers.copy()
        hex_indices[:,0] = np.round(hex_indices[:,0] - bound_min_x)
        hex_indices[:,1] = np.round(bound_max_y - hex_indices[:,1])
        print("HexFilter.hex_indices_with_out_paddings=["+str(0)+","+str(bound_max_x-bound_min_x)+"]x["+str(0)+","+str(bound_max_y-bound_min_y)+"]")
        hex_indices = hex_indices.astype(np.int32)
        hex_indices_max_x = int(max_x - bound_min_x)
        hex_indices_max_y = int(bound_max_y - min_y)
        hex_indices_min_x = int(min_x - bound_min_x)
        hex_indices_min_y = int(bound_max_y - max_y)
        print("HexFilter.hex_indices_with_paddins=["+str(hex_indices_min_x)+","+str(hex_indices_max_x)+"]x["+str(hex_indices_min_y)+","+str(hex_indices_max_y)+"]")

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
    
    def sample(self, image):
        x_hex_indices = self.hex_indices[:, 0]
        y_hex_indices = self.hex_indices[:, 1]
        hex_indices_max_x = np.max(x_hex_indices)
        hex_indices_max_y = np.max(y_hex_indices)
        hex_indices_min_x = np.min(x_hex_indices)
        hex_indices_min_y = np.min(y_hex_indices)
        pad_size_rx = max(hex_indices_max_x - self.x_size  + 1, 0)
        pad_size_ry = max(hex_indices_max_y - self.y_size  + 1, 0)
        pad_size_lx = max(-hex_indices_min_x, 0)
        pad_size_ly = max(-hex_indices_min_y, 0)
        tmp = np.pad(image, ((pad_size_ly, pad_size_ry), (pad_size_lx, pad_size_rx), (0, 0)), 'edge')
        height    , width    , _ = image.shape
        pad_height, pad_width, _ = tmp.shape
        print("HexFilter.image.ranges=[" + str(0) + "," + str(width) + "]x[" + str(0) + "," + str(height) + "]")
        print("HexFilter.pad_image.ranges=[" + str(-pad_size_lx) + "," + str(pad_width - pad_size_lx -1) + "]x[" + str(-pad_size_ly) + "," + str(pad_height - pad_size_ly - 1) + "]")
        count = x_hex_indices.shape[0]
        return np.array([ tmp[y_hex_indices[i]+pad_size_ly,x_hex_indices[i]+pad_size_lx,:] for i in range(0,count)])
    def render(self,color_web,filename = None):
        x_hex_coords = self.hex_centers[:, 0]
        y_hex_coords = self.hex_centers[:, 1]
        h_fig = plt.figure(figsize=(self.x_size/16, self.y_size/16))
        h_ax = h_fig.add_axes([0, 0, 1, 1])
        ax = hl.plot_single_lattice_custom_colors(x_hex_coords, y_hex_coords,
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

