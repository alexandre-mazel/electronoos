import os
import sys

import cv2

global_facerecognizer = None

def loadReco(path):
    global global_facerecognizer
    if global_facerecognizer != None:
        return global_facerecognizer
        
    sys.path.append("../../face_tools/")
    import facerecognition_dlib
    fr = facerecognition_dlib.FaceRecogniser()
    fr.setVerbose()
    fr.loadModels()
    fr.load(path+"recface/")
    global_facerecognizer = fr
    return global_facerecognizer
    
def learnAllImages(path):
    """
    learn all faces found in file: found an image file, if theres one face in it, then learn it
    TODO: only one face!
    """
    pathDB = path
    fr = loadReco(pathDB)
    cpt = 0
    if 1:
        listFiles = os.listdir(path)
        listFiles = sorted(listFiles)
        for numfile, f in enumerate(listFiles):
            print("INF: learnAllImages: %d/%d" % (numfile/len(listFiles) ))
            fn = path+f
            if not os.path.isfile(fn):
                continue
            if "!" in f: # do we learn some ref ? (usefull for debug!)
                continue
                
            name,ext = os.path.splitext(f)
            if not ext in [".jpg", ".png"]:
                continue
                
            name = name.lower()
            
            if fr.findUserByName(name) != None:
                print("WRN: learnAllIdent: '%s' already in base" % name)
                continue
            fr.learnFromFile(fn,name) # ne semble plus fonctionner !!! setSavePath est remis a none !
            #~ fr.continuousLearnFromFile(fn,name) essayer ca ?
            cpt += 1
            #~ if cpt > 9:
                #~ break
    #~ if 1:
    fr.save(pathDB+"recface/")
    print("INF: learnAllImages: cpt: %s" % cpt )
    
cacheImages = dict() # filename => img

def findmatch(path,im):
    fr = loadReco(path)
    ret = fr.recognise(im,bSpeedUp=False)
    facerecognition_dlib.User.rDistThreshold = 10 # choppe tout le monde !
    #ret: with ids: [id, "firstname", dist, confidence, confidence_corrected
    print("ret:%s" % ret)
    if len(ret)>0:
        for r in ret:
            if r[3]>0.1:
                print("recoFromKnown: Recognised: %s (conf:%.3f)" % (r[1],r[3]))
        reco = ret[0]
                
        if reco[0] != -1:
            filename_looksalike = r[6]
            if filename_looksalike in cacheImages:
                imlooksalike = cacheImages[filename_looksalike]
            else:
                print("loading file...")
                imlooksalike = cv2.imread(filename_looksalike)
                cacheImages[filename_looksalike] = imlooksalike
            win_name = "recognised"
            cv2.imshow(win_name,imlooksalike)
            cv2.moveWindow(win_name, 640, 0)

            #~ cv2.waitKey(10)        
        
    #~ if 1:
        #~ im = cv2.imread(filename)
        #~ im = fr._renderFaceResults(im,ret)
        #~ while im.shape[1]>1200:
            #~ im = cv2.resize(im,(0,0),fx=0.5,fy=0.5)
        #~ cv2.imshow("recognised",im)
        #~ cv2.waitKey(0)

    return ret
    
    
    
def loopwebcam(pathlearned):

    cap = cv2.VideoCapture(0) #ouvre la webcam

    while 1:
        
        ret, img = cap.read() # lis et stocke l'image dans frame
        
        #~ img = cv2.resize(img, None, fx=2,fy=2)
        
        findmatch(pathlearned,img)
        
        win_name = "webcam"
        cv2.imshow(win_name,img)
        cv2.moveWindow(win_name, 0, 0)
        
        key = cv2.waitKey(100) 
        if key == 27 or key == 'q':
            break
        
        
        #~ faces = 
    
    
    
if __name__ == "__main__":
    path = "d:/generated_portraits/"
    learnAllImages(path)
    loopwebcam(path)
    