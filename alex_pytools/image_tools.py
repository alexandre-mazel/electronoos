import cv2
import numpy as np

import cv2_tools

def countNbrDifferentColorsPix(pix):
    """
    pix is a fitz pixel map
    """    
    #~ print(pix)
    if 0:
        dictColors = {}
        for j in range(pix.h):
            print(j)
            timeBegin = time.time()
            print(pix.w)
            for i in range(pix.w):
                # 9sec:
                #~ r = pix.samples[(j*pix.w+i)*3+0]
                #~ g = pix.samples[(j*pix.w+i)*3+1]
                #~ b = pix.samples[(j*pix.w+i)*3+2]
                # 3sec:
                r,g,b=pix.samples[(j*pix.w+i)*3+0:(j*pix.w+i)*3+3]
                #~ print((r,g,b))
                k="%d_%d_%d"%(r,g,b)
                dictColors[k] = 0
            print("duration: %5.2fs" % (time.time()-timeBegin))
                
        nbrColors = len(dictColors)
    else:
        img_array=pix.samples[0:pix.h*pix.w*3]
        im = np.frombuffer(img_array,dtype=np.int8)
        im = im.reshape((pix.h,pix.w,3))
        nbrColors = countNbrDifferentColors(im)

    
    
    print("DBG: countNbrDifferentColors: count_nbr_different_colors: %s" % nbrColors )
            
    return nbrColors
    
def countNbrDifferentColors(im):
    
    # jpg compression generate more different value of a single tone
    bColorAveraging = True
    bColorAveraging = False
    
    print("DBG: countNbrDifferentColors: shape: %s" % str(im.shape))
    #~ print("first pixels: %s" %str(im[0:4,0:4]))
    if bColorAveraging:
        im = im//8 # reduce color difference
        print("DBG: countNbrDifferentColors: shape after color averaging: %s" % str(im.shape))    
        print("DBG: countNbrDifferentColors: first pixels: %s" %str(im[0:4,0:4]))
    #~ ret = np.unique(im)
    nbrChannel = 1
    if len(im.shape)>2: nbrChannel = im.shape[2]
    ret = np.unique(im.reshape(-1, nbrChannel), axis=0)
    #~ print("unique: %s" % str(ret))
    nbrColors = len(ret)
    return nbrColors

def isLookLikePhoto(im,roi,bDebug=False):
    """
    is the roi in im looks like a photo (else it can be a area of text or ...)
    - roi: if None => full image
    """
    
    if roi == None:
        roi = [0,0,im.shape[1],im.shape[0]]
    
    imc = im.copy()
    imc = imc[ max(0,roi[1]):roi[1]+roi[3] , max(0,roi[0]):roi[0]+roi[2] ]
    if len(imc.shape)>2 and imc.shape[2]>1:
        imc = cv2.cvtColor(imc,cv2.COLOR_BGR2GRAY)
    
    if 0:
        f = np.fft.fft2(imc)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20*np.log(np.abs(fshift))
        #~ magnitude_spectrum = np.abs(fshift)
        laplacian = cv2.Laplacian(np.abs(fshift),cv2.CV_64F)
        laplacian = cv2.Laplacian(magnitude_spectrum,cv2.CV_64F)
        diff = np.mean(laplacian)
        print("DBG: isLookLikePhoto: diffLapla: %.3f" % diff )
    
    laplacian = cv2.Laplacian(imc,cv2.CV_64F,ksize=3) # ksize=3
    diff2 = abs(np.mean(laplacian)*100)
    print("DBG: isLookLikePhoto: diffLapla2: %.3f" % diff2 )
    
    nNbrColor = countNbrDifferentColors(imc)
    print("DBG: isLookLikePhoto: nNbrColor: %d" % nNbrColor )

    

    if bDebug and  0:
        from matplotlib import pyplot as plt
        plt.subplot(121),plt.imshow(imc, cmap = 'gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(magnitude_spectrum, cmap = 'gray') # cmap = 'Accent'
        plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
        plt.show()

    #~ bRet = diff > 0.1
    bRet = diff2 > 20
    #~ bRet = diff2 > 150 # exploring other ksize
    
    if bDebug and 1: 
        print("DBG: isLookLikePhoto: ret: %s" % bRet )
        imc = im.copy()
        cv2.rectangle(imc,(roi[0],roi[1]),(roi[0]+roi[2],roi[1]+roi[3]), (0,120,120),1)
        cv2_tools.drawHighligthedText(imc,str(bRet),roi[0:2])
        while imc.shape[1]>640: imc = cv2.resize(imc,(0,0),fx=0.5,fy=0.5)
        cv2.imshow("isLookLikePhoto",imc)
        cv2.waitKey(0)
        
    return bRet



def autoTest():
    bDebug = 1
    bDebug = 0
    
    
    bAssert = 0
    bAssert = 1
    
    im = cv2.imread("../data/multiple_humans.jpg")
    bRet = isLookLikePhoto(im,None,bDebug=bDebug)
    
    bRet = isLookLikePhoto(im,(300,200,100,100),bDebug=bDebug)
    if bAssert: assert(bRet==0)
    
    bRet = isLookLikePhoto(im,(188, 312, 71, 85),bDebug=bDebug)
    if bAssert: assert(bRet)
    bRet = isLookLikePhoto(im,(761, 341, 73, 101),bDebug=bDebug)
    if bAssert: assert(bRet)
    bRet = isLookLikePhoto(im,(524, 293, 68, 92),bDebug=bDebug)
    if bAssert: assert(bRet)
    bRet = isLookLikePhoto(im,(1094, 373, 97, 91),bDebug=bDebug)
    if bAssert: assert(bRet)
    
    im = cv2.imread("../data/logo_target.jpg")
    bRet = isLookLikePhoto(im,None,bDebug=bDebug)
    if bAssert: assert(bRet==0)
    
    im = cv2.imread("../data/logo_intel.png")
    bRet = isLookLikePhoto(im,None,bDebug=bDebug)
    if bAssert: assert(bRet==0)
    
    im = cv2.imread("../data/logo_olympic.png")
    bRet = isLookLikePhoto(im,None,bDebug=bDebug)
    if bAssert: assert(bRet==0)
    
    
    
    
    if 0:
        cv2.imshow("image_tools",im)
        key=cv2.waitKey(1) # time for image to refresh even if continuously pressing a key
        key=cv2.waitKey(0)


if __name__ == "__main__":
    pass
    autoTest()