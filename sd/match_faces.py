import os
import sys
import time

import cv2

"""
scp a@192.168.0.45:/home/a/generated/portr* d:\generated_portraits\

sudo mount -t drvfs d: /mnt/d
rsync -rv --size-only a@192.168.0.45:/home/a/generated/portr* /mnt/d/generated_portraits/
"""

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
    import facerecognition_dlib
    facerecognition_dlib.User.rDistThreshold = 0.2 # force to learn many more people
    cpt = 0
    cptAdded = 0
    cptTooClose = 0
    if 1:
        listFiles = os.listdir(path)
        #~ listFiles = sorted(listFiles)
        listFiles = sorted(listFiles, key=lambda x: os.path.getmtime(path+x),reverse=True) # sort by most recent added
        for numfile, f in enumerate(listFiles):
            print("INF: learnAllImages: %d/%d" % (numfile,len(listFiles) ))
            fn = path+f
            if not os.path.isfile(fn):
                continue
            if "!" in f: # do we learn some ref ? (usefull for debug!)
                continue
                
            if time.time()-os.path.getmtime(path+f) > 60*60*1 and 0:
                print("INF: learnAllImages: too old, breaking")
                break
                
            name,ext = os.path.splitext(f)
            if not ext in [".jpg", ".png"]:
                continue
                
            name = name.lower()
            
            if fr.findUserByName(name) != None:
                print("WRN: learnAllIdent: already in base: '%s'" % name)
                #~ continue
                break # so we already have done this one so all next are done also
                
            ret = fr.learnFromFile(fn,name)
            print("INF: learnAllImages: learnFromFile: ret: %s" % ret)
            status = ret[0]
            if status == 2: cptAdded += 1
            if status == -3: cptTooClose += 1
            
            cpt += 1
            #~ if cpt > 9:
                #~ break
            #~ if cpt > 100:
                #~ break
    #~ if 1:
    fr.save(pathDB+"recface/")
    print("INF: learnAllImages: cpt: %s, cptAdded: %d, cptTooClose: %d" % (cpt,cptAdded,cptTooClose) )
    
cacheImages = dict() # filename => img

def findmatch(path,im):
    fr = loadReco(path)
    ret = fr.recognise(im,bSpeedUp=False)
    import facerecognition_dlib
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
            dist = r[2]
            conf = r[4]
            
            filename_looksalike = filename_looksalike.replace("/lki/", "/lki0/")
            if filename_looksalike in cacheImages:
                imlooksalike = cacheImages[filename_looksalike]
            else:
                print("INF: loading file %s" % filename_looksalike)
                imlooksalike = cv2.imread(filename_looksalike)
                cacheImages[filename_looksalike] = imlooksalike
            
            if 1:
                imlooksalike = imlooksalike.copy()
                h,w = imlooksalike.shape[:2]
                txt = "dst: %4.2f, conf: %4.2f" % (dist,conf)
                fontFace = 0
                fontScale = 0.8
                thickness = 2
                x = int(h/2)
                x = 10
                cv2.putText( imlooksalike, txt, (x, h-10 ), fontFace, fontScale, (255,255,255), thickness )
            try:
                win_name = "recognised"
                cv2.imshow(win_name,imlooksalike)
            except BaseException as err:
                print("ERR: in imshow: err: %s" % err )
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
    #~ path = "C:/Users/alexa/Downloads/lki0/"
    learnAllImages(path)
    #~ loopwebcam(path)
    