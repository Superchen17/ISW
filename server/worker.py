'''worker class

'''
from numpy.lib.type_check import imag
from scipy.io import loadmat
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

import image_registration, isw_proposed, analysis

class Worker():
    def __init__(self):
        pass

    def _get_image_from_plt(self, image):
        temp_file = 'temp.jpg'

        out = None
        plt.imsave(temp_file, image, cmap='gray')
        with open(temp_file, 'rb') as f:
            out = f.read()

        if(os.path.exists(temp_file)):
            os.remove(temp_file)    
        return out

    def handle_get_datasets(self):
        data_names = os.listdir('../dataset/')    
        return data_names

    def handle_get_preview_ir(self, dataset):
        frames = loadmat('../dataset/'+dataset, appendmat=False).get('frames')
        frames *= 255
        
        image1, image2 = frames[:,:,0], frames[:,:,1]
   
        image_before = self._get_image_from_plt(image=image1)    
        image_after = self._get_image_from_plt(image=image2)    

        return {
            'before': image_before,
            'after': image_after
        }

    def handle_get_preview_isw(self, dataset):
        frames = loadmat('../dataset/'+dataset, appendmat=False).get('frames')
        frames *= 255

        groundtruth = loadmat('../dataset/'+dataset, appendmat=False).get('img')
        groundtruth *= 255

        distorted = []
        _, _, num_frames = np.shape(frames)
        for i in range(num_frames):
            distorted.append(self._get_image_from_plt(image=frames[:,:,i]))

        try:
            groundtruth = self._get_image_from_plt(image=groundtruth)
        except:
            groundtruth= 'na'

        return {
            'distorted': distorted,
            'groundtruth': groundtruth
        }

    def run_horn_schunck(self, dataset, alpha):
        frames = loadmat('../dataset/'+dataset, appendmat=False).get('frames')
        frames *= 255
        
        image1, image2 = frames[:,:,0], frames[:,:,1]

        flow = image_registration.horn_schunck_classic(image1, image2, alpha=alpha)
        flow = np.array(flow, dtype=np.float32)
        
        ipy, ipx = np.indices(image1.shape, dtype=np.float32)
        output = cv2.remap(image1, ipx+flow[1,:,:], ipy+flow[0,:,:], interpolation=cv2.INTER_CUBIC, borderMode=2)

        mse = analysis.get_mse(output, image2)
        output = self._get_image_from_plt(output)

        return {
            'registered': output,
            'mse': mse
        }

    def run_farneback(self, dataset):
        frames = loadmat('../dataset/'+dataset, appendmat=False).get('frames')
        frames *= 255

        image1, image2 = frames[:,:,0], frames[:,:,1]

        flow = image_registration.farneback(image1, image2)
        flow = np.array(flow, dtype=np.float32)

        ipy, ipx = np.indices(image1.shape, dtype=np.float32)
        output = cv2.remap(image1, ipx-flow[:,:,0], ipy-flow[:,:,1], interpolation=cv2.INTER_CUBIC, borderMode=2) 

        mse = analysis.get_mse(output, image2)
        output = self._get_image_from_plt(output) 

        return {
            'registered': output,
            'mse': mse
        }

    def run_restore(self, dataset):
        ref, output = isw_proposed.main(dataset)

        if len(ref) == 0:
            ssim = 'na'
            psnr = 'na'
            mse = 'na'
        else:
            ssim = analysis.get_ssim(output, ref)
            psnr = analysis.get_psnr(output, ref)
            mse = analysis.get_mse(output, ref)

        output = self._get_image_from_plt(output) 

        return {
            'restored': output,
            'ssim': ssim,
            'psnr': psnr,
            'mse': mse
        }
        