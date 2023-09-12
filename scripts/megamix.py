import pygame as pg

class Megamixer:
    
    def __init__( self ):
        pg.init()
        pg.mixer.init()
        self.sounds = [None,None,None] # placeholder for loaded sound
        
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
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
                      
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == pg.KEYDOWN:     
                print("DBG: key '%s' pressed" % event.key )
                if event.key == pg.K_ESCAPE:
                    return True
                    
        return False
                
    def play( self, songFilename, nNumDeck ):        
        #~ pg.mixer.music.load(songFilename)
        #~ pg.mixer.music.play(0)
        self.sounds[nNumDeck] = pg.mixer.Sound(songFilename)
        pg.mixer.Sound.play(self.sounds[nNumDeck])
                
                
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
    mixer.play(song2,0)
    mixer.run()
    
    
runMixer()