'''analysis class to perform quantitative analysis on results

'''
from skimage.metrics import structural_similarity, mean_squared_error
import cv2
import numpy as np

def _norm_size(output, ref):
    frames_x,frames_y= np.shape(output) 
    ref = cv2.resize(ref,(frames_y,frames_x), interpolation=cv2.INTER_CUBIC)   
    return output, ref

def get_ssim(output, ref):
    output, ref = _norm_size(output, ref)
    return '{:.3f}'.format(round(structural_similarity(output, ref, data_range=255), 3))

def get_psnr(output, ref):
    output, ref = _norm_size(output, ref)
    return '{:.2f}'.format(round(cv2.PSNR(output, ref), 2))

def get_mse(output, ref):
    output, ref = _norm_size(output, ref)
    output /= 255
    ref /= 255
    return '{:.4f}'.format(mean_squared_error(output, ref))
    