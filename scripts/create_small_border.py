import os
import cv2
import numpy as np

def create_small_border_version(strPath):
    """
    take a path and create a copy small with border of all images with a _ret in it
    """
    
    bForceRecreate = 1
    bForceRecreate = 0
    
    bAddBorder = 1
    
    bAddSignature = 1
    
    
    
    if bAddSignature: 
        #~ sign = cv2.imread("../data/lamaz_signature.png",cv2.IMREAD_UNCHANGED) # load with alpha
        #~ sign = cv2.imread("../data/lamaz_signature.png", cv2.IMREAD_GRAYSCALE)
        #~ sign = cv2.imread("../data/lamaz_signature.png", cv2.IMREAD_COLOR)
        #~ sign = cv2.imread("../data/lamaz_signature.png")
        #can't load png correctly, switching to png with writing manullay by pixel
        sign = cv2.imread("../data/lamaz_signature.jpg")
        sign = cv2.resize(sign,(0,0),fx=0.5,fy=0.5, interpolation=cv2.INTER_CUBIC) # a nice smothing
        #~ sign = cv2.resize(sign,(0,0),fx=5,fy=5)
        hsign,wsign,csign = sign.shape
    
    files = sorted(os.listdir(strPath))
    for file in files:
        file = file.lower()
        if ".png" in file or ".jpg" in file:
            if not "_ret." in file:
                continue
            strNewFile = file.replace("_ret.", "_ret_sb.")
            strNewFileAbs = strPath+os.sep + strNewFile
            if os.path.isfile(strNewFileAbs) and not bForceRecreate:
                continue
            print("INF: creating '%s'" % strNewFileAbs )
            im = cv2.imread(strPath+os.sep+file)
            print("INF: original size is: %s" % str(im.shape) )
            while im.shape[1] > 1280:
                im = cv2.resize(im,(0,0),fx=0.5,fy=0.5, interpolation=cv2.INTER_CUBIC)
                
            nAdd = 0
            if bAddBorder:
                # add border
                nBlackBorder = 2 # thickness of rectangle
                nWhiteBorder = 8
                nAdd = nBlackBorder+nWhiteBorder
                h,w,c = im.shape
                nw = w+nAdd*2
                nh = h+nAdd*2
                new_image = np.zeros((nh,nw,c), np.uint8)
                new_image[nAdd:h+nAdd,nAdd:w+nAdd] = im
                
                cv2.rectangle(new_image,(0,0),(nw,nh),(255,255,255),nWhiteBorder*2) 
                
                im = new_image
                
            h,w,c = im.shape
            if bAddSignature:
                # no transp:
                #~ im[h-nAdd-hsign:h-nAdd,w-nAdd-wsign:w-nAdd] = sign
                # with weighted: (not working)
                #~ blank_image_with_signature = np.zeros((h,w,4), np.uint8)
                #~ blank_image_with_signature[h-nAdd-hsign:h-nAdd,w-nAdd-wsign:w-nAdd] = sign
                #~ im = cv2.addWeighted(im,0.4,blank_image_with_signature,0.1,0)
                
                # pix by pix (slow but sign is small so ok)
                print("INF: adding signature of %dx%d" % (wsign,hsign))
                if 0:
                    cv2.imshow("signature",sign)
                    cv2.waitKey(0)
                    exit(0)
                for j in range(hsign):
                    for i in range(wsign):
                        colsign = sign[j,i]
                        #~ print(colsign)

                        if list(colsign) != [255,255,255]:
                            #~ # si gris et que couleur plus fonce, ne pas dessiner
                            #~ im[h-nAdd-hsign+j,w-nAdd-wsign+i] = colsign
                            obs = sum(colsign)/(3*255)
                            im[h-nAdd-hsign+j,w-nAdd-wsign+i] = im[h-nAdd-hsign+j,w-nAdd-wsign+i]*obs
                
                
            print("INF: new size is: %s" % str(im.shape) )
            cv2.imwrite(strNewFileAbs, im, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            nFileSize = os.path.getsize(strNewFileAbs)
            print("INF: new file size: %.1fko" % (nFileSize/1024))
            print("")
                
                
    
    
    
    
strPath = "c:/tmp3/"
strPath = "c:/photos22/2022-07-03_-_BookAwa/"
create_small_border_version( strPath )