"""
Chatbot sample
"""
import sys
sys.path.append("../alex_pytools/" )
import misctools
sys.path.append("../../rounded-rects-pygame/" ) # for roundrects
from roundrects import round_rect
from roundrects import aa_round_rect as round_rect

import os
import pygame as pg
import pygame.freetype  # Import the freetype module.


class Agent(object):
    def __init__(self,screen_size):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
        self.screen = pg.display.set_mode(screen_size)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        
        self.w = screen_size[0]
        self.h = screen_size[1]
        

        self.imTopBanner = pg.image.load("top_banner_small.png") 
        #resize to screen (no bicubic)
        #~ s = self.imTopBanner.get_rect().size
        #~ self.imTopBanner = pg.transform.scale(self.imTopBanner, (self.w, int(self.w*s[1]/s[0])))
        
        pg.font.init() # you have to call this at the start, 

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True

    def update(self):
        pass

    def draw(self):
        #~ self.screen.blit(self.background, (0,0))
        self.screen.fill( pg.Color("lightslategrey") )
        
        self.screen.blit(self.imTopBanner, (0, 0)) 
    
        #~ myfont = pg.font.SysFont('Comic Sans MS', 30)
        #~ textsurface = myfont.render('Faiska', False, (0, 0, 0))
        myfont = pygame.freetype.SysFont('Verdana', 18)
        textsurface,rect = myfont.render('Faiska', (0, 0, 0))
        self.screen.blit(textsurface,(self.w//2-(rect[2]-rect[0])//2,6))

        #~ round_rect(self.screen, (50,20,400,200), pg.Color("darkslateblue"),
                        #~ 30, 50, pg.Color("lightslateblue"))
        #~ round_rect(self.screen, (20,235,100,200), pg.Color("red"), 10, 5)
        #~ round_rect(self.screen, (140,250,175,100), pg.Color("black"), 30,
                        #~ 2, pg.Color("green"))
        #~ round_rect(self.screen, (335,250,145,200), pg.Color("purple"), 30, 20, pg.Color("yellow"))
        
                        


    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)

#class Agent - end

def runAgent():
    a = Agent((700//2,700)) #700 is the size of my banner
    a.main_loop()
    pg.quit()
    
if __name__ == "__main__":
    runAgent()
    sys.exit()