# coding: cp1252
"""
Chatbot sample
"""
import sys
sys.path.append("../alex_pytools/" )
import misctools
sys.path.append("../../rounded-rects-pygame/" ) # for roundrects
from roundrects import round_rect
from roundrects import aa_round_rect as round_rect
import noise

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
        
        
        self.imBot = pg.image.load("robot_idle.png")
        s = self.imBot.get_rect().size
        wdst = s[0]//2
        self.imBot = pg.transform.scale(self.imBot, (wdst, int(wdst*s[1]/s[0])))
        
        self.strTxtSpeak = ""
        
        pg.font.init()


    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True

    def update(self):
        pass
        
        
    def speak(self,txt):
        self.timeStartSpeak = pg.time.get_ticks()/1000
        self.rDurationSpeak = len(txt)/10
        self.strTxtSpeak = txt
        
    def isSpeaking(self):
        return self.strTxtSpeak != ""

    def draw(self):
        #~ self.screen.blit(self.background, (0,0))
        #~ self.screen.fill( pg.Color("lightslategrey") )
        
        colBackground = (247,247,247)
        colLight1 = (220,220,220)
        colDark1 = (22,22,22)
        colBlue1 = (164,194,244)
        colBotsSkin = (243,243,243)
        colBotsMicro = (153,153,153)
        
        myfont = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 20)
        #~ myfontsmall = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 16)
        myfontsmall = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 16)
        
        
        w = self.w
        h = self.h
        
        self.screen.fill( colBackground )

        
        # system
        self.screen.blit(self.imTopBanner, (0, 0)) 
        ycur = 8
        textsurface,rect = myfontsmall.render('11:28', (0, 0, 0))
        self.screen.blit(textsurface,(10+20 ,ycur))
        
        # title
        ycur = 28
        
        for i in range(3):
            y = ycur+i*6
            pg.draw.line(self.screen, colDark1,(10,y),(30,y),2 )

    
        #~ myfont = pg.font.SysFont('Comic Sans MS', 30)
        #~ textsurface = myfont.render('Faiska', False, (0, 0, 0))
        #~ myfont = pygame.freetype.SysFont('Verdana', 18)

        textsurface,rect = myfont.render('Faiska', (0, 0, 0))
        self.screen.blit(textsurface,(w//2-(rect[2]-rect[0])//2,ycur))
        ycur = 50
        
        pg.draw.line(self.screen, colLight1,(0,ycur),(w,ycur) )
        ycur += 1
        
        
        # screen
        # roundrect(mat,(x,y,w,h),col1,round_size,border_size)
        ycur += 20
        xmargin=20
        ymargin=20
        warea = w-xmargin*2
        harea = 400
        
        xbot = xmargin+warea-self.imBot.get_rect().size[0]+xmargin//2 + 6
        ybot = ycur+harea-self.imBot.get_rect().size[1]#+ymargin//2
        
        round_rect(self.screen, (xmargin,ycur,warea,harea), colBlue1, 10, 0)
        self.screen.blit(self.imBot, (xbot, ybot))
        

        xmouth = xbot+101
        ymouth = ybot+96
        wmouth = 40
        hmouth = 30
        
        if self.isSpeaking():
            # change mouth
            pg.draw.rect(self.screen,colBotsSkin,(xmouth-wmouth//2,ymouth-hmouth//2,wmouth,hmouth) )
        
            
            rTime = pg.time.get_ticks()/1000 #rTime in sec
            
            #nMouthSize = (int(rTime)*3)%hmouth
            nMouthSize = abs(noise.getSimplexNoise(rTime*3))*hmouth
            pg.draw.ellipse(self.screen,colDark1,(xmouth-nMouthSize,ymouth-nMouthSize//2,nMouthSize*2,nMouthSize) )
            
            nEnd = int((pg.time.get_ticks()/1000-self.timeStartSpeak)*10)
            txt = self.strTxtSpeak[:nEnd]
            textsurface,rect = myfont.render(txt, (0, 0, 0))
            self.screen.blit(textsurface,(xmargin*2,ycur+ymargin))
        
        
        # microphone over mouth
        wmicro = 26
        hmicro = 16
        pg.draw.ellipse(self.screen,colBotsMicro,(xmouth-wmicro//2-26,ymouth-hmicro//2+2,wmicro,hmicro) )
        
    # draw - end


    def main_loop(self):
        while not self.done:
            self.event_loop()
            rTime = pg.time.get_ticks()/1000
            nTime = int(rTime)
            if nTime == 2 and not self.isSpeaking():
                self.speak("Compar� � votre mission pr�c�dente, le cadre de celle ci vous a t'il paru plus agr�able ?")
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