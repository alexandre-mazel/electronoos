import cv2
import numpy as np

def cleanImage(im):
    """
    clean an image
    """
    ret,im = cv2.threshold(im,127,255,cv2.THRESH_BINARY)

    if 1:
        kernel = np.ones((7,7),np.uint8)
        im = cv2.dilate(im,kernel,iterations = 4)

    return im

class Comparator:
    
    def __init__( self ):
        pass
        
        
    def compare( self, file1, file2 ):
        """
        compare two files containing images
        return similtude [0..1]: 0: image is very different, 1: same image
        """
        im1 = cv2.imread(file1,cv2.IMREAD_GRAYSCALE)
        assert(im1.shape[0]>1)
        im2 = cv2.imread(file2,cv2.IMREAD_GRAYSCALE)
        assert(im2.shape[0]>1)
        
        im1 = 255-im1
        im2 = 255-im2
        
        
        # here transform images to the same size!
        
        # here transformate to get more accurate score
        
        if 1:
            # remove grey pixels (watermarking...)
            im1=cleanImage(im1)
            im2=cleanImage(im2)
            
        if 1:
            #resizing: the smaller, the less error
            rRatio = 0.1
            im1 = cv2.resize(im1, None, fx=rRatio,fy=rRatio)
            im2 = cv2.resize(im2, None, fx=rRatio,fy=rRatio)
            
        imDiff = np.abs(im1-im2)
        
        if 1:
            # render to see what we've got
            cv2.imshow("im1",im1)
            cv2.imshow("im2",im2)
            cv2.imshow("imDiff",imDiff)
            
            cv2.waitKey(0)
        
        nNbrPointOriginal = np.sum(im1)/255
        print("nNbrPointOriginal:%d"%nNbrPointOriginal)
        nMaxDiff = nNbrPointOriginal*128
        #~ rDiff = np.sum(imDiff)/(128*im1.shape[0]*im1.shape[1])
        rDiff = (np.sum(imDiff)/128.)/float(nMaxDiff)
        print("rDiff:%5.4f"%rDiff)
        return 1.-rDiff

comparator = Comparator()
        
def auto_test():
    f1 = "fusil.jpg"
    f2 = "fusil_try1.png"
    f3 = "fusil_try2.png"
    for f in (f2,f3):
        res = comparator.compare(f1,f)
        print( "simil %s and %s => %5.4f" % (f1,f,res) )

if __name__ == "__main__":
    auto_test()