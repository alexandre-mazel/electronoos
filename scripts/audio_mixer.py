#~ import audioread
import librosa
import time

def test():
    f = "c:/tmp/poker-face-medieval-style.mp3"
    #~ a = audioread.audio_open(f)
    #~ buf = a.read_data()
    buf,samplerate = librosa.load(f,sr=None)
    print("DBG: len: %s" % len(buf))
    print("DBG: samplerate: %s" % str(samplerate))
    duration = len(buf)/samplerate/60. #seems like it's mono
    print("DBG: duration: %s" % str(duration))
    
    n = 0
    windowsize = 4096*2
    while n < len(buf)-windowsize:
        m_block = librosa.feature.melspectrogram(buf[n:n+windowsize], sr=samplerate,n_fft=2048,hop_length=2048,center=False)
        #print(m_block)
        for i in range(10):
            print(m_block[i])
        print("")
        n+=windowsize
        #~ break
        
import pygame
pg=pygame

import numpy as np

import sys
sys.path.append("../alex_pytools/")
sys.path.append("C:/Users/alexa/dev/git/electronoos/alex_pytools/")
import sound_player

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)

class Object:
    def __init__(self,x=10,y=10,w=32,h=32):
        self.x = w
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0

# class Object - end

class Sound:
    def __init__(self):
        self.datas = []
        self.pos = 0 # in s
        self.maxf = [0]*1000 # memorize old maxis for each freq
        self.timemaxf = [0]*1000
        self.maxcur = 0
        self.timemaxcur = 0
        self.bPause = False
        
    def load(self):
        print("load sound...")
        f = "c:/tmp/poker-face-medieval-style.mp3"        
        #~ f = "c:/tmp/theme-from-the-shawshank-redemption (double bass).mp3"
        f = "c:/tmp/Eminem - Mockingbird (Blasterjaxx Remix).mp3"
        self.datas,self.samplerate = librosa.load(f,sr=None)
        print("load sound - end")
        
        # so sad to read the music elsewhere
        pg.mixer.music.load(f)
        #~ offset = 0.5 # 0.5: time for the stuff to load (beurk) it was related to the BT !
        #~ offset = 1.5
        self.timeBegin = time.time()
        pg.mixer.music.play()
        
    def pause(self):
        self.bPause = not self.bPause
        if self.bPause:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()
        
    def update(self):
        self.pos = time.time()-self.timeBegin
        #~ print("DBG: Sound.update: current time: %.2fs" % self.pos)
        #~ self.pos = pg.mixer.music.get_pos()
        #~ print(pg.mixer.music.get_pos())
        
        # there's a slight difference due to buffering?
        offset = 0.5 # Tme for the stuff to load (beurk), no it was related to the BT !
        offset = -0.2
        self.pos = (pg.mixer.music.get_pos()/1000.) - offset
        if self.pos < 0:
            self.pos = 0
            
    def render(self,surface):
        bw = 8 # width of one band
        x = 20
        y = 840+30 # bottom of graph
        
        windowsize = 2048
        n = int(self.pos * self.samplerate)#+windowsize//2 # heard sound is centered to window
        
        try:
            m_block = librosa.feature.melspectrogram(self.datas[n:n+windowsize], sr=self.samplerate,n_fft=2048,hop_length=2048,center=False)
        except librosa.util.exceptions.ParameterError as err:
            print("WRN: Sound.render: err: %s" % str(err))
            return
        
        #~ print(m_block)
        S_dB = librosa.power_to_db(m_block, ref=np.max)
        #~ print(S_dB)
        for i in range(len(S_dB)):
            vol = 5+int(abs(0.5*m_block[i][0]))
            #~ vol = int( 500-abs(500.*S_dB[i][0]) )
            
            if self.bPause:
                vol = 0
                
            if vol < 0:
                vol = 0
                
            pg.draw.rect(surface,white,(x,y-vol,bw,vol))
            
            
            if self.maxf[i] < vol:
                self.maxf[i] = vol
                self.timemaxf[i] = time.time()
            elif self.maxf[i] > 0:
                self.maxf[i] -= 5*(time.time()-self.timemaxf[i])*(time.time()-self.timemaxf[i])
                pg.draw.rect(surface,gray,(x,y-self.maxf[i],bw,2))
                
            x += bw


        x += 100
        vol = self.datas[n]*500
        vol = max(self.datas[n:n+windowsize])*200
        pg.draw.rect(surface,white,(x,y-vol,bw,vol))
        if self.maxcur < vol:
            self.maxcur = vol
            self.timemaxcur = time.time()
        else:
            self.maxcur -= 5*(time.time()-self.timemaxcur)*(time.time()-self.timemaxcur)
            pg.draw.rect(surface,gray,(x,y-self.maxcur,bw,2))
        
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1280+80, 840+40))
        self.clock = pygame.time.Clock()
        self.fps = 24  # Frames per second.
        
        self.square = Object()
        self.square.img = pygame.Surface((self.square.w, self.square.h))
        self.square.img.fill(white)
        self.square.x = 0
        self.square.y = 0
        self.square.vx = 5
        
        self.keypressed={} # will store current keyboard pressed
        
        self.sounds = []
        self.sounds.append(Sound())
        self.sounds[-1].load()
        
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
                
            if event.type == pygame.KEYDOWN:     
                print("DBG: key '%s' pressed" % event.key )
                self.keypressed[event.key] = 1
                
                if event.key == 112: # p
                    self.sounds[0].pause()
                
            if event.type == pygame.KEYUP:
                self.keypressed[event.key] = 0
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                if key == pygame.K_a or key == pygame.K_UP:
                    self.square.y -= 1
                elif key == pygame.K_q or key == pygame.K_DOWN:
                    self.square.y += 1
                elif key == pygame.K_ESCAPE:
                    return True
                    
        return False
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        self.square.x += self.square.vx
        self.square.y += self.square.vy
        
        # out of screen test
        if      (self.square.vx > 0 and self.square.x + self.square.w > self.screen.get_width()) \
            or (self.square.vx < 0 and self.square.x < 0) \
            :
            self.square.vx *= -1
            
            
        self.sounds[0].update()

    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)
        self.screen.blit(self.square.img, [self.square.x,self.square.y,self.square.x+self.square.w,self.square.y+self.square.h] )
        
        self.sounds[0].render(self.screen)
        pygame.display.update()  # or pygame.display.flip()
        
# class Game - end


def runGame():
    game = Game()
    while 1:
        bQuit = game.handleInput()
        game.update()
        if bQuit:
            break
        game.render()
        
# startGame - end


if __name__ == "__main__":
    #~ test()
    runGame()