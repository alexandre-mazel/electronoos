import sys

#~ sys.path.append("../../face_tools/")(
sys.path.append("../alex_pytools/")

import face_detector_cv3
import misctools
import cv2
import random

def detect_face_big_image(im):
    """
    Si l'image est trop grosse, on la coupe hauteur et on analyse en plusieurs fois, puis on recolle les coords
    """
    bRenderDebug = 0
    print(im.shape)    
    h,w = im.shape[:2]
    ih = 0
    dh = 700
    allfaces = []
    while 1:
        faces = face_detector_cv3.facedetector.detect(im[ih:ih+dh,:],bRenderBox=False,confidence_threshold=0.26)
        print(faces)
        for face in faces:
            allfaces.append( (face[0],face[1]+ih,face[2],face[3]+ih,face[4]) )
        ih += dh
        if ih > h:
            break
            
    if bRenderDebug:
        # check detect
        for face in allfaces:
            cv2.rectangle(im,(face[0],face[1]),(face[2],face[3]), (255,0,0),3)
        im = cv2.resize(im,(0,0),fx=0.5,fy=0.5)
        cv2.imshow("check detect", im)
        key = cv2.waitKey(0)            
        
        
    return allfaces


def guess_trombi(filename):
    """
    analyse an image found faces, show one face,
    then wait a bit before printing the text below the image
    
    press esc to quit
    """
    
    im = cv2.imread(filename)
    faces = detect_face_big_image(im)

        
    timeGuess = 10
    timeGuess = 1000
    
    cpt = 0
    while 1:
        #~ idx = random.randint(0,len(faces)-1)
        idx = misctools.shuffle_int_mem(len(faces))
        print("try: %d, idx: %2s, faces[idx]: %s" % (cpt,idx,str(faces[idx])) )
        l,t,r,b,_ = faces[idx]
        
        t = t-20
        if t < 0:
            t = 0
            
        l = l-20
        if l < 0:
            l = 0            
        
        imface = im[t:b+20,l:r+20]
        imface = cv2.resize(imface,(0,0),fx=3,fy=3)
        cv2.imshow("guess who?", imface)
        key = cv2.waitKey(timeGuess)
        if key == 27: break
        
        imface = im[t:b+160,l:r+20]        
        imface = cv2.resize(imface,(0,0),fx=3,fy=3)
        cv2.imshow("guess who?", imface)
        key = cv2.waitKey(timeGuess*2)
        if key == 27: break
        
        cpt += 1

strPath = r"C:\Users\alexa\perso\docs\2024_09_Enseignement_Voltaire/"
strPath = r"C:\Users\alexa\perso\docs_nextcloud_edu\2024_09_Enseignement_Voltaire/"
fname = strPath + r"2024_09_NSI\1NSINF1_trombi_01.png"
#~ fname = strPath + r"2024_09_SNT\210_trombi_all.png"
#~ fname = strPath + r"2024_09_SNT\213_trombi_all.png"

guess_trombi(fname)