import cv2
import math
import numpy as np
import random
import sys
import time

import bleedfacedetector as fd # pip install bleedfacedetector

sys.path.append("../alex_pytools")
import misctools
import score_table

class FaceTracker:
    """
    choose a face (the most centered) then stuck on it
    """
    def __init__(self,screen_width,screen_heigth):
        # default behavior: look for the most centered
        # look for center of the face
        self.fx = screen_width//2
        self.fy = screen_heigth//2
        self.fw = 50
        self.fh = 50
        
    def update(self,faces):
        """
        Receive a list of face, find the good one and return updated information about the same face than before
        If no face, return previous one
        """
        nearest_dist = 9999999
        nearest_idx = -1
        for idx,(x, y, w, h) in enumerate(faces):
            cx = x+w/2
            cy = y+h/2
            dist = (self.fx-cx)*(self.fx-cx)+(self.fy-cy)*(self.fy-cy)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = idx
                
        if nearest_idx != -1:
            #~ print("nearest_dist: %s" % nearest_dist )
            x, y, w, h = faces[nearest_idx]
            self.fx = int(x+w/2)
            self.fy = int(y+h/2)
            self.fw = w
            self.fh = h
            
        return self.fx,self.fy,self.fw,self.fh
# FaceTracker - end
            
            

def runGame():
    
    zoom = 2

    # Load the cascade
    face_cascade = cv2.CascadeClassifier('../oia/haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0) #ouvre la webcam
    
    screen_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    screen_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print("INF: cam_fps: %s" % cam_fps )
    
    
    nCptFrame = 0
    timeFps = time.time()
    
    #  info racket
    rx = 320
    ry = 240
    sx = 70
    sy = 30
    racket_vx = 0
    racket_vy = 0
    
    # info on ball
    bx = 320
    by = 100
    vx = 0
    vy = 3
    ball_radius = 20 # radius of ball
    
    face_tracker_0 = FaceTracker(screen_w,screen_h)
    timeEndLoose = time.time() - 20
    

    score = 0
    nRank = 0
    
    nAccelerator = 0
    
    st = score_table.ScoreTable("face_racket")

    while 1:
        
        ret, img = cap.read() # lis et stocke l'image dans frame
        
        #~ img = cv2.resize(img, None, fx=2,fy=2)
        
        img = cv2.flip(img,1) # flip horiz


        timeProcess = time.time()
        # Detect faces
        
        if 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # < 0.00000s
            faces = face_cascade.detectMultiScale(gray, 1.1, 10) # 0.05s
        else:
            faces = fd.ssd_detect(img,conf=0.3) # 0.03s
        
        #~ print("DBG: time analysis: %.5fs" % (time.time()-timeProcess))

        if 0:
            # Draw rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
        old_rx = rx
        old_ry = ry
        
        if  0:
            # simpler algo, but need only one face on screen
            for (x, y, w, h) in faces:
                dw = int(0.3*w)
                #~ rx = x+int(dw)

                rx = x+w//2
                rx -=sx//2
                ry = y+int(h*0.7)

                #cv2.rectangle(img, (x+dw, y+int(h*0.7)), (x+(w-dw), y+int(h*0.8)), (255, 0, 0), -1)
        else:
            # work with many face
            rx,ry,face_w,face_h = face_tracker_0.update(faces)
            rx -=sx//2
            ry = int(ry-face_h//2+face_h*0.7)

        racket_vx = rx-old_rx
        racket_vy = ry-old_ry
        
        
        if time.time() < timeEndLoose:
            # end game sequence
            imgsave = img.copy()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            for image in [imgsave,img]:
                cv2.putText(image,"score: %d" % final_score, (10,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
            
                if nRank < 10 or 0:
                    if ((nCptFrame//3) %2) == 0:
                        cv2.putText(image,"rank : %d" % (nRank+1), (10,40+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                
            cv2.imwrite("/tmp/"+misctools.getFilenameFromTime()+".jpg", imgsave )
            
            cv2.putText(img,"Looser!", (rx-15,ry-face_h//2),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

            if 1:
                score_x = screen_w-340
                score_y = 20
                cv2.rectangle(img,(score_x-10,score_y-20),(score_x-10+300,score_y+120), (0,0,0), -1 )
                hiscore = st.get_results(10)
                hiscore = hiscore.split('\n')
                for pt,line in enumerate(hiscore):
                    line = line.replace('\t','')
                    cv2.putText( img, line, (score_x,score_y+pt*12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1 )
            img = cv2.resize(img,(0,0),fx=zoom,fy=zoom)
            cv2.imshow('img', img)
            nCptFrame += 1
            key = cv2.waitKey(1)
            if key == 27:
                break
            continue
                
        # update
        
        ball_prev_x = bx
        ball_prev_y = by
        
        if vy<0:
            vy += 0.1
        else:
            vy += 0.1
            
        bx += vx
        by += vy
        
        if bx+ball_radius > screen_w or bx-ball_radius < 0:
            # out of screen side
            vx = -vx
            
        if by-ball_radius < 0:
            vy = -vy
            
        if by+ball_radius > screen_h:
            bx = screen_w // 2
            by = ball_radius+1
            vx = (random.random()-0.5)*4
            vy = 3
            print("You loose!")
            final_score = score//10
            nRank = st.get_rank(final_score)
            print("DBG: rank: %s" % nRank)
            if nRank < 10:
                st.add_score(final_score,"")
                st.save()
                
            score = 0
            timeEndLoose = time.time()+4
            
        
        # compute intermediate position:
        nNbrIntermediate = 50
        for i in range(nNbrIntermediate+1):
            ball_test_x = ball_prev_x * (1-i/nNbrIntermediate) + bx * i/nNbrIntermediate
            ball_test_y = ball_prev_y * (1-i/nNbrIntermediate) + by * i/nNbrIntermediate
            r_test_x = old_rx * (1-i/nNbrIntermediate) + rx * i/nNbrIntermediate
            r_test_y = old_ry * (1-i/nNbrIntermediate) + ry * i/nNbrIntermediate
            
            if ball_test_x+ball_radius >= r_test_x and ball_test_x-ball_radius<r_test_x+sx and ball_test_y+ball_radius > r_test_y and ball_test_y-ball_radius < r_test_y+sy:
                # colliding
                vx += (ball_test_x-(r_test_x+sx/2))*0.1 + racket_vx/10
                
                if ball_test_y < r_test_y:            
                    vy = -abs(vy) + racket_vy/10
                    # move ball so it doesn't look into the racket
                    by = ry - ball_radius
                # else the ball continue down
                break

            
            
        score += abs(vx)+abs(vy)
        
        div500 = score // 5000
        if div500 > nAccelerator:
            print("DBG: score: %s, div500: %s, nAccelerator: %s" % (score,div500,nAccelerator) )
            vy *= 1.2
            nAccelerator = div500
            
                
        # rendering
        cv2.rectangle(img, (rx, ry), (rx+sx, ry+sy), (255, 255, 255), -1)
        cv2.circle(img, (int(bx), int(by)), ball_radius, (255, 0, 0), -1)
        cv2.putText(img,"score: %d" % (score//10), (10,40//2),cv2.FONT_HERSHEY_SIMPLEX,1/2,(255,0,0),2)
            
            
        # Display
        img = cv2.resize(img,(0,0),fx=zoom,fy=zoom)
        cv2.imshow('img', img)
        key = cv2.waitKey(1)
        
        if key == 27:
            break
            
        nCptFrame += 1
        if nCptFrame == 100:
            duration = time.time()-timeFps
            fps = nCptFrame/duration
            print("INF: fps: %.2ffps" % fps ) # 22/24 fps on suface7
            
            nCptFrame = 0
            timeFps = time.time()
            
runGame()