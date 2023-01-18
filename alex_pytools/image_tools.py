import cv2
import numpy as np
import time

import cv2_tools


def show(im):
    cv2.imshow("temp",im)
    cv2.waitKey(0)

def getRatioWB(im):
    """
    return the ratio of pixel white and black in the image
    """
    if len(im.shape)>2 and im.shape[2]>1:
        im = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    n_white_pix = np.sum(im >= 250)
    n_black_pix = np.sum(im <= 5)
    total = im.shape[0]*im.shape[1]
    return n_white_pix/total,n_black_pix/total
    

    

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
    
def countNbrDifferentColors(im,bColorAveraging=False):
    
    # jpg compression generate more different value of a single tone

    print("DBG: countNbrDifferentColors: shape: %s" % str(im.shape))
    #~ print("first pixels: %s" %str(im[0:4,0:4]))
    if bColorAveraging:
        im = im//8 # reduce color difference
        #~ print("DBG: countNbrDifferentColors: shape after color averaging: %s" % str(im.shape))    
        #~ print("DBG: countNbrDifferentColors: first pixels: %s" %str(im[0:4,0:4]))
    #~ ret = np.unique(im)
    nbrChannel = 1
    if len(im.shape)>2: nbrChannel = im.shape[2]
    ret = np.unique(im.reshape(-1, nbrChannel), axis=0)
    #~ print("unique: %s" % str(ret))
    nbrColors = len(ret)
    return nbrColors
    
def countNbrDifferentColorsSlow(im):
    
    # jpg compression generate more different value of a single tone

    print("DBG: countNbrDifferentColors: shape: %s" % str(im.shape))
    dictColor = {}
    for j in range(im.shape[0]):
        for i in range(im.shape[1]):
            pix = im[j,i]
            try:
                dictColor[pix] += 1
            except KeyError as err:
                dictColor[pix] = 1
    nbrColors =  len(dictColor)
    return nbrColors

def isLookLikePhoto(im,roi,bDebug=False):
    """
    is the roi in im looks like a photo (else it can be a area of text or ...)
    - roi: if None => full image
    """
    
    if bDebug: print("")
    
    if roi == None:
        roi = [0,0,im.shape[1],im.shape[0]]

    
    imc = im.copy()
    imc = imc[ max(0,roi[1]):roi[1]+roi[3] , max(0,roi[0]):roi[0]+roi[2] ]

    if imc.shape[1] < 1 or imc.shape[0] < 1:
        return False
        
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

    cnz = np.count_nonzero(laplacian)/(imc.shape[0]*imc.shape[1])
    #~ print("DBG: isLookLikePhoto: cnz: %s" % cnz )

    diff2 = abs(np.mean(laplacian)*100)
    if bDebug: print("DBG: isLookLikePhoto: diffLapla2: %.3f" % diff2 )
    
    if bDebug:
        nNbrColor = countNbrDifferentColors(imc)
        print("DBG: isLookLikePhoto no avg: nNbrColor: %d" % nNbrColor )

        nNbrColor2 = countNbrDifferentColors(imc,1)
        print("DBG: isLookLikePhoto avg: nNbrColor2: %d" % nNbrColor2 )  

        nNbrColor3 = countNbrDifferentColorsSlow(imc)
        print("DBG: isLookLikePhoto avg: nNbrColor3: %d" % nNbrColor3 )  
        

    rW,rB = getRatioWB(imc)
    if bDebug: print("DBG: isLookLikePhoto ratio b/w: %s" % str((rW,rB)) )       

    if bDebug and  0:
        from matplotlib import pyplot as plt
        plt.subplot(121),plt.imshow(imc, cmap = 'gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(magnitude_spectrum, cmap = 'gray') # cmap = 'Accent'
        plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
        plt.show()

    #~ bRet = diff > 0.1
    #~ bRet = diff2 > 150 # exploring other ksize
    bRet = (diff2 > 20 and rW < 0.2 and rB < 0.2) or (diff2 > 5 and rW < 0.05 and rB < 0.05)
    bRet = cnz >0.8 and bRet

    
    if bDebug and 1: 
        print("DBG: isLookLikePhoto: ret: %s" % bRet )
        imc = im.copy()
        cv2.rectangle(imc,(roi[0],roi[1]),(roi[0]+roi[2],roi[1]+roi[3]), (0,120,120),1)
        cv2_tools.drawHighligthedText(imc,str(bRet),roi[0:2])
        while imc.shape[1]>640: imc = cv2.resize(imc,(0,0),fx=0.5,fy=0.5)
        cv2.imshow("isLookLikePhoto",imc)
        cv2.waitKey(0)
        
    return bRet
    
"""
find bigger square
    class ImgProcessor:
        def __init__(self, filename):
            self.original = cv2.imread(filename)

        def imProcess(self, ksmooth=7, kdilate=3, thlow=50, thigh= 100):
            # Read Image in BGR format
            img_bgr = self.original.copy()
            # Convert Image to Gray
            img_gray= cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            # Gaussian Filtering for Noise Removal
            gauss = cv2.GaussianBlur(img_gray, (ksmooth, ksmooth), 0)
            # Canny Edge Detection
            edges = cv2.Canny(gauss, thlow, thigh, 10)
            # Morphological Dilation
            # TODO: experiment diferent kernels
            kernel = np.ones((kdilate, kdilate), 'uint8')
            dil = cv2.dilate(edges, kernel)
            cv2.namedWindow("dil", cv2.WINDOW_NORMAL)
            cv2.imshow("dil", dil)
            cv2.waitKey(0)

            return dil
        
        def largestCC(self, imBW):
            # Extract Largest Connected Component
            # Source: https://stackoverflow.com/a/47057324
            image = imBW.astype('uint8')
            nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
            sizes = stats[:, -1]

            max_label = 1
            max_size = sizes[1]
            for i in range(2, nb_components):
                if sizes[i] > max_size:
                    max_label = i
                    max_size = sizes[i]

            img2 = np.zeros(output.shape)
            img2[output == max_label] = 255
            return img2
        
        def maskCorners(self, mask, outval=1):
            y0 = np.min(np.nonzero(mask.sum(axis=1))[0])
            y1 = np.max(np.nonzero(mask.sum(axis=1))[0])
            x0 = np.min(np.nonzero(mask.sum(axis=0))[0])
            x1 = np.max(np.nonzero(mask.sum(axis=0))[0])
            output = np.zeros_like(mask)
            output[y0:y1, x0:x1] = outval
            return output

        def extractROI(self):
            im = self.imProcess()
            lgcc = self.largestCC(im)
            lgcc = lgcc.astype(np.uint8)
            roi = self.maskCorners(lgcc)
            # TODO mask BGR with this mask
            exroi = cv2.bitwise_and(self.original, self.original, mask = roi)
            return exroi

        def show_res(self):
            result = self.extractROI()
            cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
            cv2.imshow("Result", result)
            cv2.waitKey(0)
            
    ip = ImgProcessor("autotest_data/screen_linkedin.png") # pas la meilleur image pour ce test
    ip.show_res()
"""


def findPicturesInImage(im, nMinSize=16,nMaxSize=64, bRound=1):
    """
    take a big image (usually screencapture) and find picture area
    - bRound: search for round one, default look for rect.
    return a list of area (centerx,centery,warea,harea)
    """
    
    bRender = 1
    bRender = 0
    
    im = cv2.resize(im,(0,0),fx=0.5,fy=0.5,interpolation=cv2.INTER_NEAREST) # INTER_NEAREST or INTER_AREA
    
    listOut = []

    if 1:

        if bRender: out = im[:]
        searchSize = 16 # size of search chunk
        startX = 0
        startY = 0
        x = y = 0 # coord of chunk
        h,w = im.shape[:2]
        wchunk = w//searchSize +1 # +1 in case smaller than chunk
        hchunk = h//searchSize + 1
        
        store = np.zeros((hchunk,wchunk),np.uint8)
        print(store.shape)
        while 1:
        
            hist = cv2.calcHist([im[startY:startY+searchSize,startX:startX+searchSize] ],[0],None,[256],[0,256])
            #~ print(hist[:16])
            nz = np.count_nonzero(hist)
            if nz > 50:
                if bRender: print("startX:%s, startY: %s, nz: %d" % (startX,startY,nz) )
                color = (255,0,0)
                if bRender: cv2.rectangle(out,(startX,startY),(startX+searchSize,startY+searchSize), color )
                store[y,x] = 1
                
            
            startX  += searchSize
            x += 1
            if startX >= w:
                startY += searchSize
                startX = 0
                y += 1
                x = 0
                #~ print("DBG: findPicturesInImage: startY: %s" % startY )
            if startY > h:
                break
                
        # paste area
        j = 0
        while j < hchunk:
            i = 0
            while i < wchunk:
                harea = 0
                warea = 0
                if store[j,i]:
                    # find contiguous : goal: find bbox, we scan each line to find at least one litten
                    # if no litten stop
                    bAtLeastOne = 1
                    harea = 0
                    while bAtLeastOne:
                        k = 0
                        bAtLeastOne = 0
                        if j+harea+1 < hchunk and store[j+harea+1,i-1]:
                            # the pixel on the left below is on so let's decay the area
                            i -= 1
                            warea += 1
                        while i+k < wchunk:
                            if store[j+harea,i+k] == 0:
                                if k >= warea:
                                    break
                            else:
                                store[j+harea,i+k] = 0 # so we won't analyse this area latter
                                bAtLeastOne = 1
                            k += 1
                            if k > warea:
                                warea = k
                        harea += 1
                    cx = i + warea//2
                    cy = j + harea//2
                    cx *= searchSize
                    #~ cx += searchSize //2
                    
                    cy *= searchSize
                    cy -= searchSize //2
                    
                    warea *= searchSize
                    harea *= searchSize
                    harea -= searchSize
                    
                    listOut.append((cx,cy,warea,harea))
                    
                    if bRender: cv2.rectangle(out,(cx-warea//2,cy-harea//2),(cx+warea//2,cy+harea//2), (0,255,0), 3 )
                i += 1
            j += 1
                
        if bRender: show(out)
        
        print("DBG: findPicturesInImage (%d area(s)): %s" % (len(listOut),listOut) )
    return listOut

    
    #~ im = cv2.resize(im,(0,0),fx=1./nMinSize,fy=1./nMinSize)

    #~ mettre le noir en blanc (threshold?)
    #~ div par 4
    #~ cherche le nombre de couleur sur chaque rect ou faire histogram local
            
                
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cleaned = gray[:]
    ret,cleaned = cv2.threshold(cleaned,50,255,cv2.THRESH_TOZERO)
    #~ cleaned = cv2.bitwise_not(cleaned)
    #~ ret,cleaned = cv2.threshold(cleaned,100,255,cv2.THRESH_TOZERO)
    #~ ret,cleaned = cv2.threshold(cleaned,250,255,cv2.THRESH_TOZERO_INV)
    #~ cleaned = cv2.bitwise_not(cleaned)
    
    #~ gray = cv2.bitwise_not(gray)
    #~ blur = cv2.GaussianBlur(gray,(5,5),0)
    #~ ret3,cleaned = cv2.threshold(blur,240,255,cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)
    
    cleaned[np.where(cleaned==[0])] = 255
    
    show(cleaned)
    
    cleaned = cv2.resize(cleaned,(0,0),fx=1./nMinSize,fy=1./nMinSize,interpolation=cv2.INTER_NEAREST)
    
    #~ show(cleaned)
    
    if 1:
        temp = cv2.resize(cleaned,(0,0),fx=8,fy=8)
        show(temp)
        
    #~ return
    

    from scipy.ndimage import sobel
    
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    gray = gray.astype(np.float32)
    grad_x = sobel(gray, axis=1)
    grad_y = sobel(gray, axis=0)
    energy = np.abs(grad_x) + np.abs(grad_y)
    show(energy)
    
    if 0:
        #~ energy = energy.astype(np.uint8)
         
        #~ energy = cv2.convertTo(energy, CV_32SC1);
        energy = energy.astype(np.float32)
        print(energy.shape)
        print(energy.dtype)
        
        ret,thresh = cv2.threshold(gray,50,255,0)
        contours,hierarchy = cv2.findContours(thresh, 1, 2)
        print("Number of contours detected:", len(contours))

        for cnt in contours:
           x1,y1 = cnt[0][0]
           approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
           if len(approx) == 4:
              x, y, w, h = cv2.boundingRect(cnt)
              ratio = float(w)/h
              if ratio >= 0.9 and ratio <= 1.1:
                 img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
                 cv2.putText(img, 'Square', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
              else:
                 cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                 img = cv2.drawContours(img, [cnt], -1, (0,255,0), 3)

        show(img)

    
    energy = cv2.resize(energy,(0,0),fx=1./nMinSize,fy=1./nMinSize)
    #~ energy = cv2.resize(energy,(0,0),fx=1./nMinSize,fy=1./nMinSize,interpolation=cv2.INTER_AREA)

    kernel = np.ones((3, 3), np.uint8)
    energy = cv2.erode(energy, kernel)

    if 1:
        temp = cv2.resize(energy,(0,0),fx=8,fy=8)
        show(temp)
    
    
# findPicturesInImage - end
    
if 1:
    im = cv2.imread("autotest_data/screen_linkedin.png")
    timeBegin = time.time()
    findPicturesInImage(im)
    print("INF: duration: %.3fs" % (time.time()-timeBegin) ) # mstab7: 0.05s
    exit(0)



def autoTest():
    bDebug = 1
    bDebug = 0
    
    
    bAssert = 0
    bAssert = 1
    
    img = np.zeros((100,200,3), np.uint8)
    img[0:10,0:10] = 255
    img[10:20,0:10] = 127
    
    ret = getRatioWB(img)
    print("getRatioWB: %s" % str(ret))
    if bAssert: assert(ret[0]==(10*10)/(100*200))
    if bAssert: assert(ret[1]==((100*200)-200)/(100*200))    
    
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