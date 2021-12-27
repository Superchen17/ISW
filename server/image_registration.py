from scipy.io import loadmat
from scipy.signal import convolve2d
import numpy as np
import cv2

'''
image directions  --------- y
                  |       |
                  |       |
                  |       |
                  ---------
                  x

'''
dy = np.array([
    [-1, 1],
    [-1, 1]
], dtype=float)

dx = np.array([
    [-1,-1],
    [1,1]
], dtype=float)

dt = np.array([
    [1,1],
    [1,1]
], dtype=float) * 0.25

laplacian = np.array([
    [1/12, 1/6, 1/12],
    [1/6, 0, 1/6],
    [1/12, 1/6, 1/12]
], dtype=float)

def horn_schunck_classic(image1, image2, alpha=15, epsilon=0.0001, kappa=3, u=None, v=None):
    '''horn schunck optical flow algorithm

    args:
        image1 (np.ndarray): moving image.
        image2 (np.ndarray): reference image
        alpha (float): smoothness penalizer
        epsilon (float): stopping threshold
        kappa (int): arbitrary scalar (3)
        u (np.ndarray): initial x direction flow map
        v (np.ndarray): initial y direction flow map

    returns:
        u (np.ndarray): x direction flow map
        v (np.ndarray): y direction flow map

    '''
    if u is None:
        u = np.zeros_like(image1, dtype=np.float32)
    if v is None:
        v = np.zeros_like(image1, dtype=np.float32)
        
    ex = 0.25*(convolve2d(image1, dx, mode='same')+convolve2d(image2, dx, mode='same'))
    ey = 0.25*(convolve2d(image1, dy, mode='same')+convolve2d(image2, dy, mode='same'))
    et = convolve2d(image2, dt, mode='same')-convolve2d(image1, dt, mode='same')

    map_diff = np.inf
    while map_diff > epsilon**2:
        u_bar = convolve2d(u, laplacian, mode='same')
        v_bar = convolve2d(v, laplacian, mode='same')

        u_next = u_bar - ex*(ex*u_bar+ey*v_bar+et)/(kappa*alpha**2+ex**2+ey**2)
        v_next = v_bar - ey*(ex*u_bar+ey*v_bar+et)/(kappa*alpha**2+ex**2+ey**2)

        map_diff = (np.sum(np.square(u_next-u))+np.sum(np.square(v_next-v)))/(np.shape(image1)[0]*np.shape(image1)[1])
        u, v = u_next, v_next

    return u,v

def farneback(image1, image2):
    '''gunnar farneback optical flow algorithm (from cv2)

    '''
    ipy, ipx = np.indices(image1.shape, dtype=np.float32)

    flow = cv2.calcOpticalFlowFarneback(image1,image2,None,0.6,4,13,3,7,1.5,0)
    # flow = np.array(flow, dtype=np.float32)
    # output = cv2.remap(image1, ipx-flow[:,:,0], ipy-flow[:,:,1], interpolation=cv2.INTER_CUBIC, borderMode=2)  

    return flow