# Pyxel Studio

import pyxel
import heros
import monstre
import room
import arme




class App:
    def __init__(self):
        pyxel.init(128,128, title="Nuit du Code")
        self.init_pos = 56,56
        self.heros = heros.Heros(self.init_pos[0],self.init_pos[1], arme.DragonSlayer(self.init_pos[0],self.init_pos[1], self))
        self.room = room.Room()
        self.room.create()
        self.personnages = [self.heros]
        #self.personnages.append(monstre.Monstre(56,56))
        pyxel.load("2.pyxres")
        
        pyxel.run(self.update, self.draw)
        
    def update(self):
        #if pyxel.rndi(0,100) < 42:
        #    self.personnages.append(monstre.Monstre(rndi(0, self.room.w-16), pyxel.rndi(0,self.room.h-16)))
        for p in self.personnages:
            x,y = p.deplacement((self.heros.x, self.heros.y))
            if self.room.is_passable(x,y):
                p.set_new_pos(x,y)
            p.update()
        if self.room.update(self.heros.x,self.heros.y):
            self.heros.x,self.heros.y = self.init_pos[0],self.init_pos[1]
            self.personnages.append(monstre.Monstre(*self.room.get_empty_space()))


    def draw(self):
        self.room.render()
        for p in self.personnages:
            xlocal, ylocal = self.room.conv_global_to_local(p.x,p.y)
            p.draw(xlocal,ylocal)

    def attaquer(self, x, y, h, w):
        indice = 1
        while indice < len(self.personnages):
            p = self.personnages[indice]
            points = [(p.x, p.y), (p.x+16, p.y), (p.x, p.y+16), (p.x+16,p.y+16)]
            print(points)
            print(x, y, w, h)
            print(self.heros.x, self.heros.y)
            dead = False
            for px, py in points:
                if px >= x and px <= x+w and py >= y and py <= y+h:
                    dead = True
                    print("IS DEAD !!!")
            if dead:
                del self.personnages[indice]
            else:
                indice+=1



App()