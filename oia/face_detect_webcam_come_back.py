import cv2
import math
import numpy as np
import time

import sys
sys.path.append("../scripts")
import tts_say
def say(txt):
    tts_say.say(txt)

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(2) #ouvre la webcam

bAlreadyShouted = True
timeLastSeen = time.time()

while 1:

    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 10)

    if 1:
        # Draw rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
    nbr_faces = len(faces)
    if nbr_faces > 0:
        print("someone")
        timeLastSeen = time.time()
        bAlreadyShouted = False
    else:
        print("noone...")
        if not bAlreadyShouted:
            if time.time()-timeLastSeen > 1:
                bAlreadyShouted = True
                say("Hey revient gamin!")
        
    cv2.imshow('img', img)
    key = cv2.waitKey(1)
    
    if key == 27:
        break