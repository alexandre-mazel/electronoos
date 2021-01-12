import cv2
import os

def fishEye2PepperChin(im):
    """
    from my fish eye: 
    to a pepper: H55.2 / V44.3 
    """

def processImageInPath( strPathSrc, strPathDst ):
    """
    A method to process images in one folder and save them somewhere else
    Return False if user want to quit.
    
    Rappel: convert one video to png:
    ffmpeg -i in.mp4 -vsync 0 out%05d.png
    """

    listFile = sorted(  os.listdir(strPathSrc) )
    i = 0
    bContinue = True
    bRender = True
    while i < len(listFile) and bContinue:
        print("Analyse: %d/%d" % (i,len(listFile) ) )
        #~ if i < 2000:
            #~ i += 1
            #~ continue
        f = listFile[i]
        tf = strPathSrc + f
        if os.path.isdir(tf):
            bRet = processImageInPath(tf + os.sep)
            if not bRet: return bRet
            i += 1
            continue
        
        filename, file_extension = os.path.splitext(f)
        if ".png" in file_extension.lower() or ".jpg" in file_extension.lower():
            
            im = cv2.imread(tf)
            if bRender:
                cv2.imshow("processing", im)
                key = cv2.waitKey(3)
                if key == ord('q') or key == 27:
                    bContinue = False
                    break
                if key == ord('p'):
                    i -= 5 # skip also some previous file not images, like skel... - crappy!
                    if i < 0:
                        i = -1
                        
        i += 1
    # while - end
    
    return bContinue
# processImageInPath - end
    

if __name__ == "__main__":
    pathData = "/home/am/"
    if os.name == "nt":  pathData = "d:/"
    
    processImageInPath(pathData+"images_salon_debout_couche/fish/demo/",pathData+"export_processed/")