import cv2
import numpy as np

class ImagesMosaicer:
    """
    render a bunch of images, in a pretty line
    example of use
        mosaic = ImagesMosaicer()    
        mosaic.imshow("image1", im )
        mosaic.imshow("image2", im2 )
        mosaic.imshow("image3", im3 )
        ...
        mosaic.reset()
        mosaic.imshow("image1", im )
        mosaic.imshow("image2", im2 )
        mosaic.imshow("image3", im3 )
    """
    
    def __init__( self ):
        pass
        
    def reset(self):
        self.nextX = 0
        self.nextY = 0
        
    def imshow( self, strWindowName,cvim):
        cv2.imshow( strWindowName,cvim)
        cv2.moveWindow(strWindowName,self.nextX,self.nextY)
        self.nextX += cvim.shape[1]+10
        
mosaic = ImagesMosaicer()

def cleanImage(im):
    """
    clean an image
    """
    ret,im = cv2.threshold(im,127,255,cv2.THRESH_BINARY)

    if 1:
        kernel = np.ones((32,32),np.uint8)
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
        
        #~ mosaic.imshow("im1_origa",im1)        
        
        # here transform images to the same size!
        bRender = 1
        
        # here transformate to get more accurate score
        
        if 1:
            # remove grey pixels (watermarking...)
            if bRender: 
                imt = cv2.resize(im1,None,fx=0.2,fy=0.2)
                mosaic.imshow("im1_orig",imt)
                imt = cv2.resize(im2,None,fx=0.2,fy=0.2)
                mosaic.imshow("im2_orig",imt)
            im1=cleanImage(im1)
            im2=cleanImage(im2)
            
        if 1:
            #resizing: the smaller, the less error
            rRatio = 0.1
            im1 = cv2.resize(im1, None, fx=rRatio,fy=rRatio)
            im2 = cv2.resize(im2, None, fx=rRatio,fy=rRatio)
            
        imDiff = np.abs(im1-im2)
        
        if bRender:
            # render to see what we've got
            mosaic.imshow("im1",im1)
            mosaic.imshow("im2",im2)
            mosaic.imshow("imDiff",imDiff)
            
            cv2.waitKey(0)
        
        nNbrPointOriginal = np.sum(im1)/255
        print("nNbrPointOriginal:%d"%nNbrPointOriginal)
        nMaxDiff = nNbrPointOriginal*128
        rDiff = np.sum(imDiff)/(128*im1.shape[0]*im1.shape[1])
        #~ rDiff = (np.sum(imDiff)/128.)/float(nMaxDiff)
        print("rDiff:%5.4f"%rDiff)
        return 1.-rDiff

comparator = Comparator()
        
def auto_test():
    f1 = "fusil.jpg"
    f2 = "fusil_try1.png"
    f3 = "fusil_try2.png"
    for f in (f2,f3):
        mosaic.reset()
        res = comparator.compare(f1,f)
        print( "simil %s and %s => %5.4f" % (f1,f,res) )

if __name__ == "__main__":
    auto_test()