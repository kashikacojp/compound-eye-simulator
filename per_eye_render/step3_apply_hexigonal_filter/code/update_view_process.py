import cv2
import numpy as np
from .hexagonal_filter import hexagonal_filter, hexagonal_depth_gaussian_filter, hexagonal_gaussian_filter, apply_uniform_blur
import os
import time
import OpenEXR
import array
import Imath
def load_exr_depth(filename):
    print ('load_exr_depth: {}'.format(filename))
    file = OpenEXR.InputFile(filename)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    # file がRチャンネルを持っていることを確認
    if 'R' in file.header()['channels']:
        depth_str = file.channel('R', Imath.PixelType(Imath.PixelType.FLOAT))
    if 'V' in file.header()['channels']:
        depth_str = file.channel('V', Imath.PixelType(Imath.PixelType.FLOAT))
    depth_array = array.array('f', depth_str)
    depth_image = np.array(depth_array).reshape(size[1], size[0])

    return depth_image

