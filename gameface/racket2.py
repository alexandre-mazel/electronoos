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

class FacesTracker:
    """
    choose faces then stuck on them
    """
    def __init__(self,screen_width,screen_heigth,nNumObject):
        # default behavior: look for the most centered
        # look for center of the face
        self.screen_width = screen_width
        self.screen_heigth = screen_heigth
        
        self.reset(nNumObject)
        
    def reset(self,nNumObject):
        self.listPos = []
        for i in range(nNumObject):
            x = (1+i*3)*self.screen_width // (nNumObject*2)
            y = self.screen_heigth // 2
            w = 50
            h = 50  
            self.listPos.append([x,y,w,h])            
        
    def update(self,faces):
        """
        Receive a list of face, find the best pairing and return updated information about faces in the same order than before
        return a list of [x,y,w,h]
        If no face, return -1 and previous position
        """
        bDebug = 0
        if bDebug: print("DBG: FacesTracker: update: in: %s" % str(self.listPos) )
        if bDebug: print("DBG: FacesTracker: update: faces: %s" % str(faces) )
        
        # find nearest pos for each face, so if one face disappears, we won't mess another position
        newPos = self.listPos[:]
        #~ print(newPos)
        for idx,(x, y, w, h,conf) in enumerate(faces):
            cx = x+w/2 # centerx
            cy = y+h/2
            nearest_dist = 9999999999999
            nearest_i = -1
            for i in range(len(self.listPos)):
                dist = (self.listPos[i][0]-cx)*(self.listPos[i][0]-cx)+(self.listPos[i][1]-cy)*(self.listPos[i][1]-cy)
                if bDebug: print("dist: %.3f" % dist )
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_i = i
                
            if bDebug: print("DBG: FacesTracker: update: nearest_i: %s" % nearest_i )
            if nearest_i != -1:
                newPos[nearest_i]=[cx,cy,w,h]
                self.listPos[nearest_i] = [999999,999999,999999,99999] # ne selectionne plus celui ci
                
        self.listPos = newPos
        if bDebug: print("DBG: FacesTracker: update: out: %s" % str(self.listPos) )
        return self.listPos[:] # return a copy, for safety
# FacesTracker - end

class Racket:
    """
    simple object to store data
    """
    def __init__( self, x, y ):
        self.x = x #left corner
        self.y = y
        self.px = x # previous position
        self.py = y
        self.sx = 70 # size
        self.sy = 30
        self.vx = 0 # vitesse
        self.vy = 0
        
class Ball:
    """
    simple object to store data
    """
    def __init__( self, x, y ):
        self.x = x
        self.y = y
        self.px = x # previous position
        self.py = y
        self.radius = 20
        self.sy = 30
        self.vx = 0
        self.vy = 3
        
class Ground:
    """
    simple object to store data
    """
    def __init__( self, x, y, sx ):
        self.x = x # left corner
        self.y = y
        self.vx = 0
        self.vy = 0
        self.sx = sx
        self.sy = 4
        
    

            
class Game:
    def __init__( self, screen_w, screen_h,nNumPlayer ):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.zoom = 1.83
        
        self.reset(nNumPlayer)
        
    def reset( self, nNumPlayer ):
        print( "Game: Starting with %d player(s)" % nNumPlayer )        

        self.nNumPlayer = nNumPlayer
        
        
        #~ self.fts = []
        #~ self.fts.append( FaceTracker(screen_w*1/4, screen_h/2) )
        #~ if self.nNumPlayer > 1:
            #~ self.fts.append( FaceTracker(screen_w*3/4, screen_h/2) )
            
        self.ft = FacesTracker(self.screen_w, self.screen_h, nNumPlayer)
        
        self.rackets = []
        self.rackets.append( Racket(self.screen_w*1/4, self.screen_h/2) )
        if self.nNumPlayer > 1:
            self.rackets.append( Racket(self.screen_w*3/4, self.screen_h/2))
            
        self.faceInfo = [[0]*4]*2
        
        self.ball = Ball(self.screen_w/2,100)
        
        self.ground = Ground(self.screen_w//2-50,self.screen_h-4,100)

        self.timeEndLoose = time.time() - 20
        

        self.score = 0
        self.nRank = 0
        
        self.nAccelerator = 0
        
        self.scoreTable = score_table.ScoreTable("face_racket")
        
        self.nCptFrame = 0

        
    def launchEndOfGame( self ):
        self.numLooser = 0
        if self.nNumPlayer > 1 and self.ball.x > self.screen_w // 2:
            self.numLooser = 1
        self.ball.x = self.screen_w // 2
        self.ball.y = self.ball.radius + 1
        self.ball.vx = (random.random()-0.5)*4
        self.ball.vy = 3
        print("You loose!")
        self.final_score = self.score//10
        self.nRank = self.scoreTable.get_rank(self.final_score)
        print("DBG: rank: %s" % self.nRank)
        if self.nRank < 10:
            self.scoreTable.add_score(self.final_score,"")
            self.scoreTable.save()
            
        self.score = 0
        self.timeEndLoose = time.time()+4
        self.ft.reset(self.nNumPlayer)
        
    def updateBall( self ):
        
        self.ball.px = self.ball.x
        self.ball.py = self.ball.y
        
        if self.ball.vy < 0:
            self.ball.vy += 0.1
        else:
            self.ball.vy += 0.1
            
        self.ball.x += self.ball.vx
        self.ball.y += self.ball.vy
        
        if self.ball.x + self.ball.radius > self.screen_w or self.ball.x - self.ball.radius < 0:
            # out of screen on side
            self.ball.vx = -self.ball.vx
            
        if self.ball.y - self.ball.radius < 0:
            self.ball.vy = -self.ball.vy
            
        if self.ball.y + self.ball.radius > self.screen_h:
            
            if self.nNumPlayer > 1:
                if not( self.ball.x + self.ball.radius < self.ground.x or self.ball.x - self.ball.radius > self.ground.x + self.ground.sx ):
                    self.ball.vy = -self.ball.vy
                else:
                    self.launchEndOfGame()
            else:
                self.launchEndOfGame()
                
                
            
            
    def update( self, faces ):
        
        # update rackets
        
        self.faceInfo = self.ft.update(faces)
        
        for i in range(self.nNumPlayer):
            if 0:
                # when each tracker tracks only one face
                idx,x,y,w,h =  self.fts[i].update(faces)
                
                if idx != -1:
                    del faces[idx]
                self.faceInfo[i] = x,y,w,h
            else:
                x,y,w,h = self.faceInfo[i]
                
            self.rackets[i].px = self.rackets[i].x
            self.rackets[i].py = self.rackets[i].y
             
            self.rackets[i].x = int(x - self.rackets[i].sx//2)
            self.rackets[i].y = int(y-h//2+h*0.7)
            
            if self.nNumPlayer > 1:
                # block racket on each side
                if i == 0:
                    if self.rackets[i].x + self.rackets[i].sx > self.screen_w/2:
                        self.rackets[i].x = self.screen_w//2-self.rackets[i].sx
                else:
                    if self.rackets[i].x < self.screen_w/2:
                        self.rackets[i].x = self.screen_w//2             

            self.rackets[i].vx = self.rackets[i].x - self.rackets[i].px
            self.rackets[i].vy = self.rackets[i].y - self.rackets[i].py
        
        if time.time() < self.timeEndLoose:
            return
            
        self.updateBall()
            
        bCollide = False
        for i in range(self.nNumPlayer):
            if bCollide:
                break
            # compute intermediate position of both racket and ball to avoid ghost ball or racket
            nNbrIntermediate = 50
            for di in range(nNbrIntermediate+1):
                ball_test_x = self.ball.px * (1-di/nNbrIntermediate) + self.ball.x * di/nNbrIntermediate
                ball_test_y = self.ball.py * (1-di/nNbrIntermediate) + self.ball.y * di/nNbrIntermediate
                r_test_x = self.rackets[i].px * (1-di/nNbrIntermediate) + self.rackets[i].x * di/nNbrIntermediate
                r_test_y = self.rackets[i].py * (1-di/nNbrIntermediate) + self.rackets[i].y * di/nNbrIntermediate
                
                if ball_test_x+self.ball.radius >= r_test_x and ball_test_x-self.ball.radius<r_test_x+self.rackets[i].sx and ball_test_y+self.ball.radius > r_test_y and ball_test_y-self.ball.radius < r_test_y+self.rackets[i].sy:
                    # colliding
                    self.ball.vx += (ball_test_x-(r_test_x+self.rackets[i].sx/2))*0.1 + self.rackets[i].vx/10
                    
                    if ball_test_y < r_test_y:            
                        self.ball.vy = -abs(self.ball.vy) + self.rackets[i].vy/10
                        # move ball so it doesn't look into the racket
                        self.ball.y = self.rackets[i].y - self.ball.radius
                    # else the ball continue down
                    bCollide = True
                    break
            
        self.score += abs(self.ball.vx)+abs(self.ball.vy)
        
        div500 = self.score // 5000
        if div500 > self.nAccelerator:
            print("DBG: score: %s, div500: %s, nAccelerator: %s" % (self.score,div500,self.nAccelerator) )
            self.ball.vy *= 1.2
            self.nAccelerator = div500
            

    def renderLooser( self,img ):
        # end game sequence
        imgsave = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        for image in [imgsave,img]:
            cv2.putText(image,"score: %d" % self.final_score, (10,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
        
            if self.nRank < 10 or 0:
                if ((self.nCptFrame//3) %2) == 0:
                    cv2.putText(image,"rank : %d" % (self.nRank+1), (10,40+30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            
        cv2.imwrite("/tmp/"+misctools.getFilenameFromTime()+".jpg", imgsave )
        
        cv2.putText(img,"Looser!", (int(self.faceInfo[self.numLooser][0]-self.faceInfo[self.numLooser][2]//2),int(self.faceInfo[self.numLooser][1]-self.faceInfo[self.numLooser][3]*1//3)),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

        if 1:
            score_x = self.screen_w-340
            score_y = 20
            cv2.rectangle(img,(score_x-10,score_y-20),(score_x-10+300,score_y+120), (0,0,0), -1 )
            hiscore = self.scoreTable.get_results(10)
            hiscore = hiscore.split('\n')
            for pt,line in enumerate(hiscore):
                line = line.replace('\t','')
                cv2.putText( img, line, (score_x,score_y+pt*12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1 )

        return img
        
    def render( self, img ):
        """
        return False if must exit game
        """
        
        if time.time() < self.timeEndLoose:
            img = self.renderLooser(img)
        else:
            if self.nNumPlayer > 1: cv2.rectangle(img, (self.ground.x, self.ground.y), (self.ground.x+self.ground.sx, self.ground.y+self.ground.sy), (170, 170, 170), -1)
            for i in range(self.nNumPlayer):
                cv2.rectangle(img, (self.rackets[i].x, self.rackets[i].y), (self.rackets[i].x+self.rackets[i].sx, self.rackets[i].y+self.rackets[i].sy), (255, 255, 255), -1)
            cv2.circle(img, (int(self.ball.x), int(self.ball.y)), self.ball.radius, (255, 0, 0), -1)
            cv2.putText(img,"score: %d" % (self.score//10), (10,40//2),cv2.FONT_HERSHEY_SIMPLEX,1/2,(255,0,0),2)
                
        img = cv2.resize(img,(0,0),fx=self.zoom,fy=self.zoom)
        cv2.imshow('Racket Face Game', img)
        
        self.nCptFrame += 1

        key = cv2.waitKey(1)
        return key != 27

# class Game - end
            

def runGame():

    cap = cv2.VideoCapture(0) #ouvre la webcam
    
    screen_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    screen_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print("INF: cam_fps: %s" % cam_fps )
    
    nNumPlayer = 1
    ret, img = cap.read()
    faces = fd.ssd_detect(img,conf=0.3)
    if len(faces)>1:
        nNumPlayer = 2
    game = Game(screen_w,screen_h,nNumPlayer)
    
    
    nCptFrame = 0
    timeFps = time.time()

    while 1:
        
        ret, img = cap.read() # lis et stocke l'image dans frame
        
        img = cv2.flip(img,1) # flip horiz


        timeProcess = time.time()
        # Detect faces
        
        if 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # < 0.00000s
            faces = face_cascade.detectMultiScale(gray, 1.1, 10) # 0.05s
        else:
            faces = fd.ssd_detect(img,conf=0.3,returnconf=True) # 0.03s
            print("DBG: faces: %s" % str(faces))
            # TODO: ici on pourrait enlever un visage si on en a plus que de joueurs, et qu'il y en a un avec bien moins de conf.
            # par exemple quand j'etais seul, j'ai eu ca:
            # DBG: faces: [[267, 210, 111, 126, 0.98029757], [283, 214, 77, 73, 0.34878302]]
        
        #~ print("DBG: time analysis: %.5fs" % (time.time()-timeProcess))

        if 0:
            # Draw rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        game.update(faces)
        
        if not game.render(img):
            break

            
        nCptFrame += 1
        if nCptFrame == 100:
            duration = time.time()-timeFps
            fps = nCptFrame/duration
            print("INF: fps: %.2ffps" % fps ) # 22/24 fps on suface7
            
            nCptFrame = 0
            timeFps = time.time()
            
runGame()