'''Proposed Method: Hierarchical Fusion

'''
import cv2
from scipy.io import loadmat
import matplotlib.pyplot as plt
import numpy as np, math
from scipy import linalg
import pywt
import time

def load_image(file_name, frame_num):
    '''load image from .mat file
    
    args:
      file_name (str): path of file on google drive

    returns:
      frames (np.ndarray): sequence of frames

    '''
    frames = loadmat(file_name, appendmat=False).get('frames')
    frames *= 255

    frames_ori = frames
    for _ in range((frame_num//60)):
        frames = np.concatenate((frames,frames_ori), axis=2)
    frames = frames[:,:,0:frame_num] 

    frames_x,frames_y,_ = np.shape(frames) 
    if(frames_x%2 == 1):
        frames_x += 1
    if(frames_y%2 == 1):
        frames_y += 1        
    frames = cv2.resize(frames,(frames_y,frames_x), interpolation=cv2.INTER_CUBIC)   

    return frames

def fuseCoeff(cooef1, cooef2):
    '''wavelet fusion of a pair of subimages using PCA

    args:
      cooef1 (np.ndarray): subimage1
      cooef2 (np.ndarray): subimage2

    returns:
      cooef (np.ndarray): fused subimage

    '''
    cooef = []    
    img1 = np.abs(cooef1).flatten()
    img2 = np.abs(cooef2).flatten()    
    img1 = img1 - np.mean(img1)
    img2 = img2 - np.mean(img2)
    
    img = []
    img.append(img1)
    img.append(img2)

    cov = np.cov(img)
    w,v = linalg.eigh(cov)
    idx = np.argsort(w)
    idx = idx[::-1]
    v = v[:,idx]
    w = w[idx]    
    v_max = np.abs(v[:,0])
   
    weight = v_max[0]/np.sum(v_max)   

    cooef = weight*cooef1+(1-weight)*cooef2
    return cooef

def waveletFuse(input1,input2):
    '''wavelet fusion

    args:
      input1 (np.ndarray): input image 1
      input2 (np.ndarray): input image 2

    returns:
      fusedImage (np.ndarray): fused image
    
    '''
    wavelet = 'bior1.1'
    cooef1 = pywt.wavedec2(input1, wavelet, level=4)
    cooef2 = pywt.wavedec2(input2, wavelet, level=4)
    
    fusedCooef = []
    for i in range(len(cooef1)):    
        if(i == 0):  
            fusedCooef.append(fuseCoeff(cooef1[0],cooef2[0])) #LL            
        else:
            c1 = fuseCoeff(cooef1[i][0],cooef2[i][0]) #LH 
            c2 = fuseCoeff(cooef1[i][1],cooef2[i][1]) #HL
            c3 = fuseCoeff(cooef1[i][2],cooef2[i][2]) #HH                                              
            fusedCooef.append((c1,c2,c3))                
    fusedImage = pywt.waverec2(fusedCooef, wavelet)        
    return fusedImage

def backDewarping(input, shiftRuleX, shiftRuleY, upscalar=2):
    '''image warping with upscaling

    '''
    frames_x_ori, frames_y_ori = np.shape(input)
    input = cv2.resize(input,(frames_y_ori*upscalar,frames_x_ori*upscalar), interpolation=cv2.INTER_CUBIC) 
    shiftRuleX = cv2.resize(shiftRuleX,(frames_y_ori*upscalar,frames_x_ori*upscalar), interpolation=cv2.INTER_CUBIC)*upscalar 
    shiftRuleY = cv2.resize(shiftRuleY,(frames_y_ori*upscalar,frames_x_ori*upscalar), interpolation=cv2.INTER_CUBIC)*upscalar
    output = np.zeros_like(input)

    mx, my = np.indices(input.shape,  dtype=np.float32)

    output = cv2.remap(input,my-shiftRuleY,mx-shiftRuleX,interpolation=cv2.INTER_CUBIC,borderMode=2)
    output = cv2.resize(output,(frames_y_ori,frames_x_ori),interpolation=cv2.INTER_CUBIC)     
    return output 


def flowEstimation(target,moving):
    '''half step image registration

    args:
      target (np.ndarray): target image
      moving (np.ndarray): moving image

    returns:
      warped (np.ndarray): generated middle image

    '''
    # ipy, ipx = np.indices(moving.shape, dtype=np.float32)

    flow_mt = cv2.calcOpticalFlowFarneback(moving, target,None,0.5,3,13,3,7,1.5,0)
    flow_mt = np.array(flow_mt, dtype=np.float32)/2
    # warped_mt = cv2.remap(moving, ipx-flow_mt[:,:,0], ipy-flow_mt[:,:,1], interpolation=cv2.INTER_CUBIC, borderMode=2)  
    warped_mt = backDewarping(moving, flow_mt[:,:,1], flow_mt[:,:,0])


    flow_tm = cv2.calcOpticalFlowFarneback(target, moving,None,0.5,3,13,3,7,1.5,0)
    flow_tm = np.array(flow_tm, dtype=np.float32)/2
    # warped_tm = cv2.remap(target, ipx-flow_tm[:,:,0], ipy-flow_tm[:,:,1], interpolation=cv2.INTER_CUBIC, borderMode=2)   
    warped_tm = backDewarping(target, flow_tm[:,:,1], flow_tm[:,:,0])

    warped = waveletFuse(warped_mt,warped_tm)  
    return warped

def processStack(frames):
    '''core method

    args:
      frames (np.ndarray): input distorted sequence

    returns:
      output (np.ndarray): restored image
      
    '''
    frames_x, frames_y, frames_z = np.shape(frames)  
    
    counter = 1
    maxLevel = math.ceil(math.log2(frames_z))
    while(frames_z>1):
        print("Level", counter, "/", maxLevel)
        
        frames_new = np.zeros((frames_x,frames_y,math.ceil(frames_z/2)))
        for i in range(0,frames_z-1,2):
            moving = frames[:,:,i]
            target = frames[:,:,i+1] 

            warped = flowEstimation(target,moving)
            frames_new[:,:,i//2] = warped

            if(i == frames_z-3):
                frameTemp = flowEstimation(frames[:,:,-1],frames[:,:,-2])
                frames_new[:,:,(i//2)+1] = frameTemp       
        
        frames = frames_new
        frames_x, frames_y, frames_z = np.shape(frames)  
        counter += 1
    output = frames[:,:,0]
   
    return output

def main(dataset):
    frames = load_image('../dataset/'+dataset, 64)
    
    try:
        ref = loadmat('../dataset/'+dataset, appendmat=False).get('img')
        ref *= 255
    except:
        ref = 'na'
        
    output = processStack(frames)

    return ref, output

if __name__ == "__main__":
    frames = load_image('../dataset/expdata_middle.mat', 64)

    tic = time.time()
    output = processStack(frames)
    toc = time.time()

    print(round(toc-tic, ndigits=2), 'seconds')
    plt.imshow(output, cmap='gray')
    plt.show()  
    