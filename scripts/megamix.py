import pygame as pg

class Megamixer:
    
    def __init__( self ):
        pg.init()
        pg.mixer.init()
        self.sounds = [None,None,None] # placeholder for loaded sound
        self.sound_vol = [0.7,0.7,0.7]
        
        w = 800
        h = 600
        if 0:
            # reduce screen to see debug
            w = 640
            h = 480
        self.screen = pg.display.set_mode((w,h))
        self.ws = self.screen.get_width()
        self.hs = self.screen.get_height()
        
        self.clock = pg.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.keypressed={} # will store current keyboard pressed
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        
        # define keys for each player
        
        listConfigKeys = [
                            # vol up, vol down
                            [pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT,pg.K_EXCLAIM], # bank 1
                            [pg.K_z,pg.K_s,pg.K_q,pg.K_d,pg.K_a], # bank 2
                      ]
                      
                      
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == pg.KEYDOWN:    
                key = event.key
                print("DBG: key '%s' pressed" % key )
                        
                self.keypressed[key] = 1
                
                if event.key == pg.K_ESCAPE:
                    return True
                    
                for nNumDeck,configkey in enumerate(listConfigKeys):
                    key_up, key_down = configkey[:2]
                    if key == key_down:
                        print("vol down")
                        self.sound_vol[nNumDeck] -= 0.1
                        self.sounds[nNumDeck].set_volume(self.sound_vol[nNumDeck]) 
                    elif key == key_up:
                        print("vol up")
                        self.sound_vol[nNumDeck] += 0.1
                        self.sounds[nNumDeck].set_volume(self.sound_vol[nNumDeck])      
                
                
            if event.type == pg.KEYUP:
                self.keypressed[event.key] = 0
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                pass
                    
        return False
                
    def play( self, songFilename, nNumDeck ):        
        #~ pg.mixer.music.load(songFilename)
        #~ pg.mixer.music.play(0)
        self.sounds[nNumDeck] = pg.mixer.Sound(songFilename)
        pg.mixer.Sound.play(self.sounds[nNumDeck])
        self.sounds[nNumDeck].set_volume(self.sound_vol[nNumDeck])
                
                
    def update( self ):
        if pg.mixer.music.get_busy():
            pg.time.Clock().tick(10)
        
        
    def run( self ):
        while not self.handleInput():
            self.update()
            
# class Megamixer - end
                

    
def runMixer():
    mixer = Megamixer()
    song1 = 'd:/mp3s/Adele - HelloLacrimosa (Mozart)The Piano Guys.mp3'
    song2 = 'd:/mp3s/abcd_deutsch_01.mp3'
    mixer.play(song1,0)
    mixer.play(song2,1)
    mixer.run()
    
    
runMixer()