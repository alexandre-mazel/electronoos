import cv2
import os

def fishEye2PepperChin(im):
    """
    from my fish eye: H106 / V180
    to a pepper: H55.2 / V44.3 
    """
    h,w,n = im.shape
    w2 = int(w / 106*55.2)
    #~ h2 = int(h / 180*44.3)
    h2 = int(w2/640*480)
    print("%dx%d => %dx%d" % (w,h,w2,h2) )
    hs = (h//2)-(h2//2)
    ws = (w//2)-(w2//2)
    print("ws:%d, hs: %d" % (ws,hs) )
    im2 = im[hs:hs+h2,ws:ws+w2]
    return im2
    

def processImageInPath( strPathSrc, strPathDst ):
    """
    A method to process images in one folder and save them somewhere else
    Return False if user want to quit.
    
    Rappel: convert one video to png:
    ffmpeg -i in.mp4 -vsync 0 out%05d.png
    """
    try: os.makedirs(strPathDst)
    except: pass
    listFile = sorted(  os.listdir(strPathSrc) )
    i = 0
    bContinue = True
    bRender = False

    cv2.namedWindow('src')
    cv2.moveWindow('src',20,20)
    
    cv2.namedWindow('dst')
    cv2.moveWindow('dst',640,20)

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
            im2 = fishEye2PepperChin(im)
            cv2.imwrite(strPathDst+f, im2)
            if bRender:
                cv2.imshow("src", im)
                cv2.imshow("dst", im2)
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