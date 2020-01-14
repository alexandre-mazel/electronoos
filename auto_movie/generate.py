
import cv2
import numpy as np
import os

def generate(strPath):
    wrender=320
    hrender=240
    s = np.zeros((hrender,wrender,3), dtype=np.int8)
    listImg = sorted(os.listdir(strPath))
    nCpt = 0
    for f in listImg:
        print("f:%s" % f )
        filename = strPath+f
        im = cv2.imread(filename)
        xl,xr = 0,1000
        yt,yb = 0,1000
        for i in range(200):
            s = im[yt+i*10:yb+i*10,xl:xr]
            cv2.imshow("f",s)
            cv2.waitKey(1)
        nCpt += 1
    
    
    
generate("D:/temp_photo_pour_auto_montage/")