import pyxel
import math
import random

class Monstre:
    def __init__(self,x,y,d=1,fr=0):
        self.x=x
        self.y=y
        self.d=0
        self.fr=0
        self.bloc = 0
        
        
    def degat(self):
        if self.bloc == 0:
            self.bloc = 30
            
            
    def deplacement(self, coord_heros):
        if self.bloc > 0:
            return self.x, self.y
        xh, yh = coord_heros
        
        dx=self.x-xh
        dy=self.y-yh
        if math.sqrt(dx**2+dy**2)<50:
            angle=math.atan2(dx,dy)
            x = self.x - math.sin(angle)
            y = self.y - math.cos(angle)
            if dx<0 :
                self.d=1
            else :
                self.d=0
        else :
            x = self.x + random.choice([-1,0,1])
            y = self.y + random.choice([-1,0,1])
            if x>0:
                self.d=1
            else :
                self.d=0
        return int(x+0.5),int(y+0.5)
    """
    def vision():
    """    
    
    def set_new_pos(self, x,y):
        self.x = x
        self.y = y
        
    def frame(self):
        if (pyxel.frame_count)%15==0:
            #~ print("dadsad")
            self.fr=(self.fr + 1)%3
             
    def update(self):
        if self.bloc > 0:
            self.bloc -= 1
        self.frame()

    def draw(self, xlocal, ylocal):
        if self.fr==0:
            if self.d==1:
                pyxel.blt(xlocal, ylocal, 0, 64, 16, 16, 16, 2)
            else :
                pyxel.blt(xlocal, ylocal, 0, 64, 16, -16, 16, 2)   
            
        if self.fr==1:
            if self.d==1:
                pyxel.blt(xlocal, ylocal, 0, 80, 16, 16, 16, 2)
            else :
                pyxel.blt(xlocal, ylocal, 0, 80, 16, -16, 16, 2)
        
        if self.fr==2:
            if self.d==1:
                pyxel.blt(xlocal, ylocal, 0, 96, 16, 16, 16, 2)
            else :
                pyxel.blt(xlocal, ylocal, 0, 96, 16, -16, 16, 2)
        
        if self.fr==3:
            if self.d==1:
                pyxel.blt(xlocal, ylocal, 0, 112, 16, 16, 16, 2)
            else :
                pyxel.blt(xlocal, ylocal, 0, 112, 16, -16, 16, 2)
