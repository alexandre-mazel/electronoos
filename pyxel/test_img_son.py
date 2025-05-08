import pyxel
import time

transp_color = 5
bank = 0

class App:
    def __init__(self):
        pyxel.init(128, 128, title="Nuit du Code")
        self.rect_x = 0
        self.rect_y = 0
        self.mov_dir = 0 # -1 to the left, +1: to the right
        self.mov_dy = 0
        
        
        
        if 0:
            # play une pattern
            for snd in range(2):
                print("snd: %d" % snd )
                pyxel.play(ch=0, snd=snd)
                time.sleep(10)
                
            pyxel.playm(0)
        
        pyxel.load("2.pyxres",excl_sounds=False)

                
        pyxel.sounds[0].set_notes("G2B-2D3R RF3F3F3")
        phrase1 = "E2B2C2D2C2B2A2 A2C2E2D2C2B2 C2D2E2C2A2A2 D2F2A2G2F2E2 C2E2D2C2B2 B2C2D2E2C2A2A2"
        phrase2 = "E2C2D2B2C2A2B#2B2"
        phrase3 = "E2E2A2A2B#2E2A2 D2D2C2C2E2E2A2"
        notes = phrase1*2+phrase2
        #~ notes = phrase3
        style_son = "P"
        pyxel.sounds[0].set_notes(notes)
        pyxel.sounds[0].set_tones(style_son*6*8) # T/S/P/N
        
        pyxel.sounds[1].set_notes(phrase3)
        pyxel.sounds[1].set_tones(style_son*6*8)
        
        pyxel.sounds[3].set_tones("P"*6*8)
        
        pyxel.play(ch=0, snd=0)
        #~ pyxel.play(ch=1, snd=1)
        

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.mov_dir = 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.mov_dir = -1
            
        if pyxel.btn(pyxel.KEY_SPACE):
            self.mov_dy = -8
            pyxel.play(ch=0, snd=3)
            
        if pyxel.btnr(pyxel.KEY_RIGHT) or pyxel.btnr(pyxel.KEY_LEFT) :
            self.mov_dir = 0
            
        self.rect_x = (self.rect_x + self.mov_dir) % pyxel.width
        
        self.rect_y+= self.mov_dy
        if self.mov_dy != 0:
            self.mov_dy += 1
        if self.rect_y < pyxel.height-16:
           self.rect_y += 2


    def draw(self):
        pyxel.cls(1)
        #pyxel.rect(self.rect_x, 0, 8, 18, 15) # x, y, w, h, color
        #num_anim = (pyxel.frame_count//30)%2
        if self.mov_dir == 0:
            num_anim = 0
            dir = 1
        else:            
            num_anim=1
            if (pyxel.frame_count//2)%2:
                num_anim=3
            dir = self.mov_dir
        
        u = 0
        v = 9*8
        pyxel.bltm(0,96,0,u,v,64,64,transp_color)
        pyxel.blt(self.rect_x, self.rect_y, bank, 0+num_anim*16, 8, 16*dir, 16, transp_color)
        
    def run(self):
        pyxel.run(self.update, self.draw)
         
app = App()
app.run()