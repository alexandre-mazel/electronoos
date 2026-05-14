import pyxel


class Arme:
    
    def __init__(self, x, y, app):
        self.x = x
        self.y = y
        self.cd = 0
        self.app = app
        
        
    def update(self):
        if self.cd > 0:
            self.cd -= 1
        
class DragonSlayer(Arme):      

    def attaque(self, d):
        self.cd = 20
        if d == 0:
            self.app.attaquer(self.x-4, self.y-16, 24, 8)
        elif d == 1:
            self.app.attaquer(self.x+16, self.y-4, 8, 24)
        elif d == 2:
            self.app.attaquer(self.x-4, self.y+16, 24, 8)
        elif d == 3:
            self.app.attaquer(self.x-16, self.y-4, 8, 24)

  

    def draw(self, x, y, d):
        if d == 0:
            if self.cd == 0:
                pyxel.blt(x, y, 0, 16, 64, -16, 16,2)
            else:
                if self.cd > 10:
                    pyxel.blt(x+8, y-4, 0, 48, 64, 16, 16,2, rotate = -90, scale = 1.5)
                pyxel.blt(x+16, y, 0, 16, 64, 16, 16,2)
        if d == 1:
            if self.cd == 0:
                pyxel.blt(x , y , 0, 16, 64, 16, 16,2)
            else:
                if self.cd > 10:
                    pyxel.blt(x+4 , y+8 , 0, 48, 64, 16, -16,2, scale = 1.5)
                pyxel.blt(x , y+16 , 0, 16, 64, 16, -16,2)
        if d == 2:
            if self.cd == 0:
                pyxel.blt(x , y , 0, 16, 64, 16, -16,2)
            else:
                if self.cd > 10:
                    pyxel.blt(x-8 , y+4 , 0, 48, 64, -16, -16,2, rotate = -90, scale = 1.5)
                pyxel.blt(x-16 , y , 0, 16, 64, -16, -16,2)
        if d in [3]:
            if self.cd == 0:
                pyxel.blt(x , y , 0, 16, 64, -16, 16,2)
            else:
                if self.cd > 10:
                    pyxel.blt(x-4 , y+8 , 0, 48, 64, -16, -16,2, scale = 1.5)
                pyxel.blt(x , y+16 , 0, 16, 64, -16, -16,2)