#~ import audioread
import librosa

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

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
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
        
    def load(self):
        print("load sound...")
        f = "c:/tmp/poker-face-medieval-style.mp3"
        self.datas,self.samplerate = librosa.load(f,sr=None)
        print("load sound - end")
        
    def update(self,surface):
        
    def render(self,surface):
        bw = 32
        x = 0
        y = 200
        
        n = 0
        windowsize = 4096*2
        m_block = librosa.feature.melspectrogram(self.datas[n:n+windowsize], sr=self.samplerate,n_fft=2048,hop_length=2048,center=False)
        print(m_block)
        for i in range(4):
            pg.draw.rect(surface,white,(x,y,bw,5+int(10*m_block[0][i])))
            x += bw

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((720, 480))
        self.clock = pygame.time.Clock()
        self.fps = 60  # Frames per second.
        
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