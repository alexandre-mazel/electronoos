import cv2
import datetime
import math
import numpy as np
import os
import time

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum( ((imageA.astype("int16") - imageB.astype("int16")) ** 2) ) # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return abs(err)
    
def getFilenameFromTime(timestamp=None):
  """
  get a string usable as a filename relative to the current datetime stamp.
  eg: "2012_12_18-11h44m49s049ms"
  
  timestamp : time.time()
  """
  # old method:
  #~ strTimeStamp = str( datetime.datetime.now() );
  #~ strTimeStamp = strTimeStamp.replace( " ", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ".", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ":", "m" );
  if timestamp is None:
      datetimeObject = datetime.datetime.now()
  elif isinstance(timestamp, datetime.datetime):
      datetimeObject = timestamp
  else:
      datetimeObject = datetime.datetime.fromtimestamp(timestamp)
  strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
  if os.name != "nt": strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no datas for microseconds on some platforms
  return strTimeStamp;
# getFilenameFromTime - end


cap = cv2.VideoCapture(1) #ouvre la EOS

width = 4000
height = 4000
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FPS,60) # ne change rien!?!
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


# warmup
for i in range(4):
    ret, img = cap.read() # lis et stocke l'image dans frame

print("img shape: %s" % str(img.shape))

strDestPath = "/images_recorded/"
try: os.makedirs(strDestPath)
except FileExistsError:pass

cpt = 0
timeBegin = time.time()
imgPrev = img
while 1:
    
    ret, img = cap.read() # lis et stocke l'image dans frame
    
    #~ img = cv2.resize(img, None, fx=2,fy=2)
    
    #~ img = cv2.flip(img,0) # flip vertic
    
    if (img == imgPrev).all():
        #~ print("DBG: same image")
        #~ print(".")
        time.sleep(0.01)
        continue
    
    diff = mse(imgPrev,img)
    #~ print("DBG: ret: %d, mse_diff :%.4f" % (ret,diff) )
    imgPrev = img
    
    if diff > 30 and 1:
        print("diff: %.4f" % diff)
        filename = strDestPath + getFilenameFromTime() + ".png"
        print( "INF: saving to '%s'" % filename ) 
        cv2.imwrite(filename,img)

    if 1:
        # Display the output
        cv2.imshow('img', img)
    key = cv2.waitKey(1)
    
    if key == 27:
        break
        
        
    cpt += 1
    if (cpt %200) == 1:
        fps = cpt/(time.time()-timeBegin)
        print("fps: %.1ffps" % (fps) )
    