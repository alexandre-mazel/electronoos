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

def renderTxtMultiline(surface, text, pos, font, color=pygame.Color('black'), nWidthMax = -1):
    """
    nWidthMax: limit width to a specific size
    """
    #~ print("DBG: renderTxtMultiline: text: %s, pos: %s, font: %s, color: %s" % (str(text),str(pos),str(font),str(color)) )
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    #space = font.size(' ')[0]  # The width of a space.
    
    #~ TODO: compute M and q and text with é
    textsurface,rect = font.render(" ")
    space = rect[2]
    wLetter = rect[2]
    hLetter = rect[3]

    #~ textsurface,rect = font.render("MqéQ")
    #~ wLetter = max(rect[2],wLetter)
    #~ hLetter = max(rect[3],hLetter)
    
    max_width, max_height = surface.get_size()
    if nWidthMax != -1: max_width = nWidthMax

    font.pad = True # render letter in a empty rect of the size of the bigger letter (even if no bigger letter to be rendered yet)

    if 1:
        x, y = pos
        for line in words:
            for word in line:
                word_surface, rect = font.render(word, color)
                word_width, word_height = rect[2],rect[3]
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row
    else:
        # redo same with precompute without rendering, then render
        # not usefull when using font.pad !!!
        lines = [""]
        x, y = pos
        for line in words:
            for word in line:
                word_surface, rect = font.render(word, color)
                word_width, word_height = rect[2],rect[3]
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                    lines.append(word + " ")
                else:
                    lines[-1] += " " + word
                x += word_width + space
            x = pos[0]  # Reset the x.

        x,y = pos
        for line in lines:
            print(font.pad)
            font.pad = True
            line_surface, rect = font.render(line, color)
            surface.blit(line_surface, (x, y+hLetter-rect[3]))
            y += int(rect[3]*1.4)
# renderTxtMultiline - end

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
        
        
    def speak(self,txt,astrAnswers):
        self.timeStartSpeak = pg.time.get_ticks()/1000
        self.rDurationSpeak = len(txt)/20
        self.strTxtSpeak = txt
        self.astrAnswers = astrAnswers
        
    def isSpeaking(self):
        return self.strTxtSpeak != ""
        
    def renderUserButton( self, astrButton, surface, pos ):
        colTxt = (243,243,243)
        colButton = (164//2,194//2,244//2)
        font = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 14)
        font.pad = True
        x, y = pos
        nMarginX = 18
        nMarginY = 2
        
        bAlignCenter = 1
        computedSize = []
        for txt in astrButton:
            txt_surface, rect = font.render(txt, colTxt)
            #~ print(rect)
            if len(txt)<0 and 0:
                nRealMarginX = 20
            else:
                nRealMarginX = nMarginX
            wButton = rect[2] + nRealMarginX*2
            hButton = rect[3] + nMarginY*2
            if not bAlignCenter:
                round_rect(surface,(x,y,wButton,hButton),colButton,11,0)
                surface.blit(txt_surface,(x+nRealMarginX,y+nMarginY))
            else:
                computedSize.append((x,y,wButton,hButton,nRealMarginX,nMarginY))
            x += wButton + nMarginX
            
        if bAlignCenter:
            # render after all computation
            # center them
            max_width, max_height = surface.get_size()
            hspace = max_width-nMarginX*2
            for data in computedSize:
                hspace-=data[2]
            hspace //= len(astrButton)-1
            #~ print("hspace: %s" % hspace )
                
            for i,txt in enumerate(astrButton):
                x,y,wButton,hButton,nRealMarginX,nMarginY = computedSize[i]
                txt_surface, rect = font.render(txt, colTxt)
                x -= nMarginX*(i)
                if i > 0:
                    x += hspace*(i)
                round_rect(surface,(x,y,wButton,hButton),colButton,11,0)
                surface.blit(txt_surface,(x+nRealMarginX,y+nMarginY))
                
     # renderUserButton - end
        

    def draw(self):
        #~ self.screen.blit(self.background, (0,0))
        #~ self.screen.fill( pg.Color("lightslategrey") )
        
        colBackground = (247,247,247)
        colLight1 = (220,220,220)
        colDark1 = (22,22,22)
        colBlue1 = (164,194,244)
        colBotsSkin = (243,243,243)
        colBotsMicro = (153,153,153)
        
        fontSys = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 20)
        #~ fontSysSmall = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 16)
        fontSysSmall = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 16)
        
        
        w = self.w
        h = self.h
        
        self.screen.fill( colBackground )

        
        # system
        self.screen.blit(self.imTopBanner, (0, 0)) 
        ycur = 8
        textsurface,rect = fontSysSmall.render('11:28', (0, 0, 0))
        self.screen.blit(textsurface,(10+20 ,ycur))
        
        # title
        ycur = 28
        
        for i in range(3):
            y = ycur+i*6
            pg.draw.line(self.screen, colDark1,(10,y),(30,y),2 )

    
        #~ fontSys = pg.font.SysFont('Comic Sans MS', 30)
        #~ textsurface = fontSys.render('Faiska', False, (0, 0, 0))
        #~ fontSys = pygame.freetype.SysFont('Verdana', 18)

        #~ fontSys.underline = True
        textsurface,rect = fontSys.render('TestPepper', (0, 0, 0))
        self.screen.blit(textsurface,(w//2-(rect[2]-rect[0])//2,ycur))
        ycur = 50
        
        pg.draw.line(self.screen, colLight1,(0,ycur),(w,ycur) )
        ycur += 1
        
        
        # screen
        # round_rect(mat,(x,y,w,h),col1,round_size,border_size)
        ycur += 20
        xmargin=20
        ymargin=20
        warea = w-xmargin*2
        harea = 500
        
        xbot = xmargin+warea-self.imBot.get_rect().size[0]+xmargin//2 + 6
        ybot = ycur+harea-self.imBot.get_rect().size[1]#+ymargin//2
        
        round_rect(self.screen, (xmargin,ycur,warea,harea), colBlue1, 10, 0)
        self.screen.blit(self.imBot, (xbot, ybot))
        

        xmouth = xbot+101
        ymouth = ybot+96
        wmouth = 40
        hmouth = 30
        
        if self.isSpeaking() and pg.time.get_ticks()/1000-self.timeStartSpeak < self.rDurationSpeak:
            # change mouth
            pg.draw.rect(self.screen,colBotsSkin,(xmouth-wmouth//2,ymouth-hmouth//2,wmouth,hmouth) )
        
            
            rTime = pg.time.get_ticks()/1000 #rTime in sec
            
            #nMouthSize = (int(rTime)*3)%hmouth
            nMouthSize = int(abs(noise.getSimplexNoise(rTime*3))*hmouth)
            pg.draw.ellipse(self.screen,colDark1,(xmouth-nMouthSize,ymouth-nMouthSize//2,nMouthSize*2,nMouthSize) )
        
        if self.isSpeaking():
            # render question
            nEnd = int((pg.time.get_ticks()/1000-self.timeStartSpeak)*20)
            txt = self.strTxtSpeak[:nEnd]
            for i in range(nEnd,len(self.strTxtSpeak)):
                if self.strTxtSpeak[i] != ' ':
                    txt += "_"
                else:
                    txt += " "
            renderTxtMultiline( self.screen, txt, (xmargin*2,ycur+ymargin-5),fontSys, colDark1,nWidthMax=300)
            ycur += harea+20
        
            # microphone over mouth
            wmicro = 26
            hmicro = 16
            pg.draw.ellipse(self.screen,colBotsMicro,(xmouth-wmicro//2-26,ymouth-hmicro//2+2,wmicro,hmicro) )

            if nEnd >= len(self.strTxtSpeak):
                self.renderUserButton( self.astrAnswers, self.screen, (xmargin,ycur) )

        
        ycur=650
        
        # progression
        round_rect(self.screen, (xmargin,ycur,warea,20), colLight1, 2, 0)
        rProgress = 0.6 
        round_rect(self.screen, (xmargin,ycur,int(warea*rProgress),20), colBlue1, 2, 0)
        
    # draw - end


    def main_loop(self):
        listQ = []
        listQ.append(["Comparé à votre mission précédente, celle ci vous a t'il paru plus agréable?", ["Oui", "Bof", "Non"]])
        listQ.append(["Sur quel aspect pensez vous cela?", ["Le cadre", "Les collégues", "Le manager", "un peu tout"]])
        nNumQ = 0
        print(listQ)
        
        while not self.done:
            self.event_loop()
            rTime = pg.time.get_ticks()/1000
            nTime = int(rTime)
            if nTime == 2 and not self.isSpeaking():
                #~ self.speak()
                self.speak( listQ[nNumQ][0],listQ[nNumQ][1])
                #~ self.speak("C?", ["Oui", "bof", "Non", "car","or"])
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