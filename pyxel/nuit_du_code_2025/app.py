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
        self.win = False
        self.personnages = [self.heros]
        #self.personnages.append(monstre.Monstre(56,56))
        pyxel.load("2.pyxres",excl_sounds=False)
        
        pyxel.run(self.update, self.draw)
        
    def update(self):
        if self.heros.vie < 0.1:
            return
        #if pyxel.rndi(0,100) < 42:
        #    self.personnages.append(monstre.Monstre(rndi(0, self.room.w-16), pyxel.rndi(0,self.room.h-16)))
        for p in self.personnages:
            x,y = p.deplacement((self.heros.x, self.heros.y))
            if self.room.is_passable(x,y):
                p.set_new_pos(x,y)
            p.update()
        ret_update = self.room.update(self.heros.x,self.heros.y)
        if ret_update == 1:
            self.heros.x,self.heros.y = self.init_pos[0],self.init_pos[1]
            self.personnages.append(monstre.Monstre(*self.room.get_empty_space()))
        elif ret_update == 2:
            self.heros.degat()
            pyxel.play(ch=0, snd=3)
        elif ret_update == 3:
            self.win = True
        self.morsure()

    def screen_lost(self):
        pyxel.cls(8)
        for i in range(10):
            msg = "YOU LOOSE!"
            pyxel.text(44+5*pyxel.sin(pyxel.frame_count-1),50+20*pyxel.sin((pyxel.frame_count-1)*10),msg, 0)
            pyxel.text(44+5*pyxel.sin(pyxel.frame_count),50+20*pyxel.sin(pyxel.frame_count*10),msg, 15)
            
    def screen_win(self):
        pyxel.cls(5)
        for i in range(10):
            msg = "YEAH!!!\nYOU GOT YOUR SLIP BACK\n WELL DONE !"
            pyxel.text(24+5*pyxel.sin(pyxel.frame_count-1),50+20*pyxel.sin((pyxel.frame_count-1)*10),msg, 0)
            pyxel.text(24+5*pyxel.sin(pyxel.frame_count),50+20*pyxel.sin(pyxel.frame_count*10),msg, 9)
        

    def draw(self):
        if self.heros.vie < 0.1:
            self.screen_lost()
            #~ self.screen_win()
            if pyxel.play_pos(0) == None: pyxel.play(ch=0, snd=2)
            return
        if self.win:
            self.screen_win()
            return
            
        self.room.render()
        for p in self.personnages:
            xlocal, ylocal = self.room.conv_global_to_local(p.x,p.y)
            p.draw(xlocal,ylocal)
        for i in range(int(self.heros.vie)):
            pyxel.blt(0+i*16, 0, 0, 112, 48, 16, 16, 2)

    def attaquer(self, x, y, h, w):
        indice = 1
        while indice < len(self.personnages):
            p = self.personnages[indice]
            points = [(p.x, p.y), (p.x+16, p.y), (p.x, p.y+16), (p.x+16,p.y+16)]
            #~ print(points)
            #~ print(x, y, w, h)
            #~ print(self.heros.x, self.heros.y)
            dead = False
            for px, py in points:
                if px >= x and px <= x+w and py >= y and py <= y+h:
                    dead = True
                    self.heros.vie += 1
                    #~ print("IS DEAD !!!")
            if dead:
                del self.personnages[indice]
            else:
                indice+=1
                
    def morsure(self):
        for p in self.personnages[1:]:
            points = [(p.x, p.y), (p.x+16, p.y), (p.x, p.y+16), (p.x+16,p.y+16)]
            dead = False
            for px, py in points:
                if px >= self.heros.x and px <= self.heros.x+16 and py >= self.heros.y and py <= self.heros.y+16:
                    #~ print("AIE!!!")
                    self.heros.degat()
                    if pyxel.play_pos(0) == None:  pyxel.play(ch=0, snd=4)
                    p.degat()



App()
