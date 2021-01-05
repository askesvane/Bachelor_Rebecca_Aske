# -*- coding: utf-8 -*-
"""
Created on Mon May  8 15:29:15 2017

@author: semkt
"""

# import the necessary packages
#venv /Users/rebeccakjeldsen/Desktop
#python3 -m /Users/rebeccakjeldsen/Desktop
#source /Users/rebeccakjeldsen/Desktop/bin/activate

import matplotlib, scipy, numpy, six
import cython

!pip import scikit-image

from skimage.measure import structural_similarity as ssim
#pip install scikit-image
#import skimage



import numpy as np
import pandas as pd
import cv2
import glob
import re

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
    return err
 
def compare_images(imageA, imageB):
	# compute the mean squared error and structural similarity
	# index for the images
    m = mse(imageA, imageB)
    s = ssim(imageA, imageB)
    return m,s 
    
### load the images -- the originals and copies to compare

# path to folders    
#ORIG_path = 'fake_pictures/'
#COPY_path = 'all_pics_tilmaj_2017/'
ORIG_path = 'C:/Users/askes/Dropbox/Bachelor - Aske og Rebecca/data_analysis/Bachelor_Rebecca_Aske/images_compare_test/originals'
COPY_path = 'C:/Users/askes/Dropbox/Bachelor - Aske og Rebecca/data_analysis/Bachelor_Rebecca_Aske/images_compare_test/copies'

# index for labels
ORIG_idx = len(ORIG_path)
COPY_idx = len(COPY_path)

# get file names
files_orig = glob.glob(ORIG_path + '*.png')
files_copy = glob.glob(COPY_path + '*.png')

# prepare panda to write logs
columns = ['ID', 'master', 'copy', 'time', 'MSE', 'SSIM']
index = np.arange(0)
DATA = pd.DataFrame(columns=columns, index = index)
 
# loop through originals and copies to compare and measure similarity 
for orig in files_orig:
    for copy in files_copy:
        # get labels (without path and extension) for match check
        orig_select = re.split('\.', orig[ORIG_idx:-1])[0]   # Medium_1_a.png
        copy_select = re.split('_c', copy[COPY_idx:-1])[0]   # Old_1_a_c27_p1_transmission_id77
        
        # check if they match
        if orig_select == copy_select:
            original = cv2.imread(orig)
            contrast = cv2.imread(copy)
            
            # convert the images to grayscale
            original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
            
            # run similarity measures
            MSE, SSIM = compare_images(original, contrast)
            
            # get id label
            id = re.findall('id\d+', copy)[0]
            
            # write output to pandas
            DATA = DATA.append({
                'ID': id, 
                'master': orig[ORIG_idx:-4],
                'copy': copy[COPY_idx:-4],
                'time': orig[ORIG_idx:-8],
                'MSE': MSE,
                'SSIM': SSIM}, ignore_index=True)

# save pandas
logfilename = 'SimilarityData2.csv'
DATA.to_csv(logfilename)            
