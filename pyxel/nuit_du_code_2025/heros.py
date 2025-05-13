import pyxel

class Heros:
    
    def __init__(self, x, y, arme=None, v = 2):
        self.x = x
        self.y = y
        self.v = v
        self.d = 2
        self.arme = arme
        self.vie = 4
        self.iframe = 0
        
    def degat(self):
        if self.iframe == 0:
            self.vie -= 1
            self.iframe = 30
        
    def deplacement(self, _):
        x = self.x
        y = self.y
        
        if pyxel.btn(pyxel.KEY_UP):
            y -= self.v
        if pyxel.btn(pyxel.KEY_DOWN):
            y += self.v
        if pyxel.btn(pyxel.KEY_LEFT):
            x -= self.v
        if pyxel.btn(pyxel.KEY_RIGHT):
            x += self.v
                
        return x,y
               
    def set_new_pos( self, x, y ):
        self.x = x
        self.y = y
        if self.arme:
            self.arme.x = x
            self.arme.y = y
            
            
    def attaquer(self):
        if self.arme.cd == 0:
            if pyxel.btnp(pyxel.KEY_E):
                self.d = 0
                self.arme.attaque(self.d)
            elif pyxel.btnp(pyxel.KEY_F):
                self.d = 1
                self.arme.attaque(self.d)
            elif pyxel.btnp(pyxel.KEY_D):
                self.d = 2
                self.arme.attaque(self.d)
            elif pyxel.btnp(pyxel.KEY_S):
                self.d = 3
                self.arme.attaque(self.d)
            
    
            
    def update(self):
        if self.iframe > 0:
            self.iframe -= 1
        self.attaquer()
        self.arme.update()
        
    def draw(self,x,y):
        if self.d == 1:
            pyxel.blt(x, y, 0, 0, 16, 16, 16, 2)
            if self.arme : 
                self.arme.draw(x+12,y-4, self.d)
        elif self.d == 2:
            pyxel.blt(x, y, 0, 160, 16, 16, 16, 2)
            if self.arme : 
                self.arme.draw(x+12,y+12, self.d)
        elif self.d == 3:
            pyxel.blt(x, y, 0,0,16,-16, 16, 2)
            if self.arme : 
                self.arme.draw(x-12, y-4, self.d)
        else:
            if self.arme : 
                self.arme.draw(x-8, y-4, self.d)
            pyxel.blt(x, y, 0, 144, 16, -16, 16, 2)