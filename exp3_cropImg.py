from PIL import Image
import pandas as pd
import glob, os, random


#### NOW WE MAKE IT AS A LOOP

# import all pics 
STIMULI = glob.glob('*png')
print(STIMULI)


for stim in STIMULI:
    screenshot_name = 'refit_' + stim
    im = Image.open(stim)
    x = im.size[0]
    y = im.size[1]
    right = (x/2)-140 
    top = (y/2)-140
    left = (x/2)+140
    bottom = (y/2)+140
    im2 = im.crop((right,top,left,bottom))
    gray = im2.convert('L')
    bw = gray.point(lambda x: 0 if x<217 else 255, '1')
    bw.save(screenshot_name)





