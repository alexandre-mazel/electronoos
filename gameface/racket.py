import cv2
import math
import numpy as np

def runGame():

    # Load the cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0) #ouvre la webcam

    while 1:
        
        ret, img = cap.read() # lis et stocke l'image dans frame
        
        #~ img = cv2.resize(img, None, fx=2,fy=2)
        
        #~ img = cv2.flip(img,0) # flip vertic

        # Convert into grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 10)

        if 1:
            # Draw rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        # Display the output
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break
            
runGame()