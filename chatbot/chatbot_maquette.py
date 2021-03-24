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

import math
import noise
import random
import time

import os
import pygame as pg
import pygame.freetype  # Import the freetype module.

def rectRotated( surface, color, pos, fill, border_radius, rotation_angle, rotation_offset_center = (0,0), nAntialiasingRatio = 1 ):
        """
        - rotation_angle: in degree
        - rotation_offset_center: moving the center of the rotation: (-100,0) will turn the rectangle around a point 100 above center of the rectangle,
                                             if (0,0) the rotation is at the center of the rectangle
        - nAntialiasingRatio: set 1 for no antialising NB: very costly due to transparency per pixel of big area and ... on my MSTab4: rendering 4 rect at 8 => 4.9fps, at 4: 15fps (timing when we were rendered at max(w,h)*max(w,h)
        """
        bDebug = 0
        nRenderRatio = nAntialiasingRatio
        
        # We need to add margin depending of the shape of the rectangle and the offset to center of rotation
        
        # idea: render everything around center of surface then copy the surface
        # render_margin is then half size of surface
        
        # intermediate rendering surface size
        # it's important to find the smaller one to avoid bliting and scaling too much pixels
        sw = pos[2]+abs(rotation_offset_center[0])*2
        sh = pos[3]+abs(rotation_offset_center[1])*2

        surfcenterx = sw//2
        surfcentery = sh//2
        s = pg.Surface( (sw*nRenderRatio,sh*nRenderRatio) )
        s = s.convert_alpha()
        s.fill((0,0,0,0))
        if bDebug: s.fill((127,127,127))
        
        rw2=pos[2]//2 # halfwidth of rectangle
        rh2=pos[3]//2

        pg.draw.rect( s, color, ((surfcenterx-rw2-rotation_offset_center[0])*nRenderRatio,(surfcentery-rh2-rotation_offset_center[1])*nRenderRatio,pos[2]*nRenderRatio,pos[3]*nRenderRatio), fill*nRenderRatio, border_radius=border_radius*nRenderRatio )
        if bDebug: pg.draw.rect(s,(0,0,0),(surfcenterx*nRenderRatio,surfcentery*nRenderRatio,2*nRenderRatio,2*nRenderRatio)) # draw center to debug
        s = pygame.transform.rotate( s, rotation_angle )        
        if nRenderRatio != 1: s = pygame.transform.smoothscale(s,(s.get_width()//nRenderRatio,s.get_height()//nRenderRatio))
        incfromrotw = (s.get_width()-sw)//2
        incfromroth = (s.get_height()-sh)//2
        surface.blit( s, (pos[0]-surfcenterx+rotation_offset_center[0]+rw2-incfromrotw,pos[1]-surfcentery+rotation_offset_center[1]+rh2-incfromroth) )
        
    
def splitTextMultiline( strLongText, nNbrLetterMax = 20 ):
    """
    Insert "\n" in a long text
    - strLongText: a long text, who can already include some \n
    """
    words = [word.split(' ') for word in strLongText.splitlines()]
    print(words)
    out = ""
    
    for j in range(len(words)):
        txt = ""
        line = words[j]
        for word in line:
            if len(txt)+len(word)>nNbrLetterMax:
                out += txt
                if txt != "":
                    out += "\n"
                txt = word
            else:
                if txt != "":
                    txt += " "
                txt += word
        out += txt
        if j < len(words)-1:
            out += "\n"
            
    print("out: '%s'" % out)
    return out
    

def renderTxtMultiline(surface, text, pos, font, color=pygame.Color('black'), nWidthMax = -1):
    """
    nWidthMax: limit width to a specific size
    return the rect
    """
    bVerbose = False
    if bVerbose: print("DBG: renderTxtMultiline: text: %s, pos: %s, font: %s, color: %s, nWidthMax=%s" % (str(text),str(pos),str(font),str(color),nWidthMax) )
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
    
    rectTotal = [pos[0],pos[1],0,0]
    if 1:
        x, y = pos
        for line in words:
            for word in line:
                word_surface, rect = font.render(word, color)
                word_width, word_height = rect[2],rect[3]
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                    rectTotal[3]+=word_height
                surface.blit(word_surface, (x, y))
                x += word_width + space
                rectTotal[2] = max(rectTotal[2],(x-space)-pos[0])
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row
            rectTotal[3]+=word_height
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
            
    if bVerbose: print("DBG: renderTxtMultiline: rectTotal: " + str(rectTotal) )
    return rectTotal
# renderTxtMultiline - end

def renderTxtMultilineCentered(surface, text, pos, font, color=pygame.Color('black'), nWidthMax = -1, nWidthTotal = -1, nHeightTotal = -1):
    """
    - nWidthMax: limit width to a specific size
    - nWidthTotal: nWidthTotal: max space to render
    return the rect
    """
    bVerbose = False
    if bVerbose: print("DBG: renderTxtMultilineCentered: text: %s, pos: %s, font: %s, color: %s, nWidthMax: %s, nWidthTotal: %s, nHeightTotal: %s" % (str(text),str(pos),str(font),str(color),nWidthMax,nWidthTotal, nHeightTotal) )
     
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    
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
    
    lines = []
    rectTotal = [pos[0],pos[1],0,0]
    x, y = pos
    for line in words:
        lines.append("")
        for nNumWord,word in enumerate(line):
            word_surface, rect = font.render(word, color)
            word_width, word_height = rect[2],rect[3]
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
                rectTotal[3]+=word_height
                lines.append("")
            x += word_width + space
            rectTotal[2] = max(rectTotal[2],(x-space)-pos[0])
            lines[-1] += word
            if nNumWord < len(line)-1:
                lines[-1] += " "
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row
        rectTotal[3]+=word_height
        
    x, y = pos
    if bVerbose: print("DBG: renderTxtMultilineCentered: lines: %s" % lines)
    if bVerbose: print("rectTotal: " + str(rectTotal) )
    if nWidthTotal  == -1: nWidthTotal=rectTotal[2]
    if nHeightTotal  == -1: nHeightTotal=rectTotal[3]
    for line in lines:
        line_surface, rect = font.render(line, color)
        if bVerbose: print("rect: %s, hLetter:%s" % (str(rect),hLetter) )
        # we assume each line has the same rect (thanks to pad option)
        xl = x + ( nWidthTotal//2 - rect[2]//2 )
        yl = y + ( nHeightTotal//2 - rectTotal[3]//2 )
        surface.blit(line_surface, (xl, yl+hLetter-rect[3]))
        y += rect[3]
        
    #~ pg.draw.rect(surface, (200,0,200),(pos[0],pos[1],rectTotal[2],rectTotal[3]) )
    #~ pg.draw.rect(surface, (255,0,255),(pos[0],pos[1],nWidthTotal,nHeightTotal) )
        
    
    return rectTotal
# renderTxtMultilineCentered - end

class Button(object):
    def __init__( self, txt, pos, size, margin, id=-1 ):
        """
        - margin: spaces between button and text
        """
        print("DBG: Button(%s,pos:%s,size:%s,margin:%s" % (txt,str(pos),str(size),str(margin)) )
        self.txt = txt
        self.pos = pos
        self.size = size
        self.margin = margin
        
    def render( self, surface, font, bSelected=False ):
        """
        return painted rect position
        """
        colTxt = (243,243,243)
        colButton = (164//2,194//2,244//2)
        colButtonSelected = (250//2,250//2,244//2)
        
        if bSelected:
            colButton = colButtonSelected
        
        #~ txt_surface, rect = font.render(self.txt, colTxt)
        round_rect(surface,self.pos+self.size,colButton,11,0)
        #~ surface.blit(txt_surface,(self.pos[0]+self.margin[0],self.pos[1]+self.margin[1]))
        renderTxtMultilineCentered(surface,self.txt,(self.pos[0],self.pos[1]),font, colTxt,nWidthTotal = self.size[0], nHeightTotal=self.size[1])
        
    def isOver(self,pos):
        if          pos[0] >= self.pos[0] and pos[0] < self.pos[0]+self.size[0] \
            and  pos[1] >= self.pos[1] and pos[1] < self.pos[1]+self.size[1] \
            :
            return True
        return False
# class Button - end

class ButtonManager(object):
    def __init__(self):
        self.aButtons = []
        self.font = None
        self.fontSmall = None
        self.nNumSelected = -1 # num of selected button; -1 => none
        
    def hasButtons( self ):
        return len(self.aButtons) > 0
        
    def createButtons( self, astrButton, surface, pos ):
        """
        surface is used just to know the available size
        """
        if self.font == None:
            self.font = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 15)
            self.font.pad = True
        if self.fontSmall == None:
            self.fontSmall = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 12)
            self.fontSmall.pad = True
            
        font = self.font
        if len(astrButton)>3:
            font = self.fontSmall
            
        x, y = pos
        nMarginX = 18
        nMarginY = 2
        
        bAlignCenter = 1
        
        self.bVerticalRender = False
        if 0: # if there's one big text
            self.bVerticalRender=True # TODO: finish to debug that: currently bug in yVertical computation
            
        computedSize = []
        for nNumButton,txt in enumerate(astrButton):
            #~ txt_surface, rect = self.font.render(txt)
            rect = renderTxtMultiline(surface,txt,pos,font,nWidthMax=surface.get_size()[0]-pos[0])
            print("DBG: ButtonManager.createButtons: rect:%s" % str(rect) )
            if len(txt)<0 and 0:
                nRealMarginX = 20
            else:
                nRealMarginX = nMarginX
            wButton = rect[2] + nRealMarginX*2
            hButton = rect[3] + nMarginY*2
            if not bAlignCenter:
                #~ round_rect(surface,(x,y,wButton,hButton),colButton,11,0)
                #~ surface.blit(txt_surface,(x+nRealMarginX,y+nMarginY))
                self.aButtons.append( Button(txt,(x,y),(wButton,hButton),(nRealMarginX,nMarginY)) )
            else:
                computedSize.append((x,y,wButton,hButton,nRealMarginX,nMarginY))
            x += wButton + nMarginX
            
        if bAlignCenter:
            # render after all computation
            # center them
            max_width, max_height = surface.get_size()
            hspace = max_width-nMarginX*2
            hMax = 0
            for data in computedSize:
                hspace -= data[2]
                hMax = max(hMax,data[3])
            hspace //= len(astrButton)-1
            #~ print("hspace: %s" % hspace )
                
            yVertical = 0
            for nNumButton,txt in enumerate(astrButton):
                x,y,wButton,hButton,nRealMarginX,nMarginY = computedSize[nNumButton]
                #~ txt_surface, rect = self.font.render(txt, colTxt)
                x -= nMarginX*(nNumButton)
                if nNumButton > 0:
                    x += hspace*(nNumButton)
                #~ round_rect(surface,(x,y,wButton,hButton),colButton,11,0)
                #~ surface.blit(txt_surface,(x+nRealMarginX,y+nMarginY))
                if self.bVerticalRender:
                    y += yVertical
                    yVertical += hButton+nMarginY*1
                    x = nRealMarginX
                self.aButtons.append( Button(txt,(x,y),(wButton,hMax),(nRealMarginX,nMarginY)) )
                
     # createButtons - end
     
    def render(self, surface):
        font = self.font
        if len(self.aButtons)>3:
            font = self.fontSmall
        for nNum,button in enumerate(self.aButtons):
            button.render(surface,font,self.nNumSelected == nNum)
            
    def isOver(self,pos):
        for nNum,button in enumerate(self.aButtons):
            if button.isOver(pos):
                return nNum
        return None
            
    def select(self,nNum,bState=True):
        self.nNumSelected = nNum
        
    def clearButtons( self ):
        self.aButtons = []
        self.nNumSelected = -1

# class ButtonManager - end
    
    
    
    
######################################################################    
            

class Agent(object):
    def __init__(self,screen_size):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "TRUE"
        self.screen = pg.display.set_mode(screen_size)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.bQuick = False # when user click it render the question directly
        
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
        self.bInBlink = False
        self.timeBotsStartExit = 0
        
        self.rAngleArm1 = 0
        
        self.strTxtSpeak = ""
        
        self.buttonManager = ButtonManager()
        
        pg.font.init()


    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True
                    
            if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                num = self.buttonManager.isOver(pos)
                if num != None:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        self.buttonManager.select(num)
                    else:
                        self.receiveAnswer(num)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.bQuick = True
                

    def update(self):
        pass
        
        
    def speak(self,txt,astrAnswers):
        self.timeStartSpeak = pg.time.get_ticks()/1000
        self.rDurationSpeak = len(txt)/20
        self.strTxtSpeak = txt
        for i in range(len(astrAnswers)):
            astrAnswers[i] = splitTextMultiline(astrAnswers[i],12)
        self.astrAnswers = astrAnswers
        
    def isSpeaking(self):
        return self.strTxtSpeak != ""
    
    def renderUserButton( self, surface, pos ):
        if not self.buttonManager.hasButtons():
            self.buttonManager.createButtons(self.astrAnswers,surface,pos)
        self.buttonManager.render(surface)
        
    def receiveAnswer(self,num):
        self.nNumQ += 1
        self.buttonManager.clearButtons()
        self.strTxtSpeak = ""
        

    def draw(self):
        #~ self.screen.blit(self.background, (0,0))
        #~ self.screen.fill( pg.Color("lightslategrey") )
        
        colBackground = (247,247,247)
        colLight1 = (220,220,220)
        colBlack = (0,0,0)
        colDark1 = (22,22,22)
        colBlue1 = (164,194,244)
        colBotsSkin = (243,243,243)
        colBotsMicro = (153,153,153)
        
        fontSys = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 20)
        #~ fontSysSmall = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 16)
        fontSysSmall = pygame.freetype.Font("../fonts/SF-Compact-Text-Semibold.otf", 15)
        fontTxt = pygame.freetype.Font("../fonts/SF-UI-Display-Regular.otf", 20)
        
        
        w = self.w
        h = self.h
        
        self.screen.fill( colBackground )

        
        # system
        self.screen.blit(self.imTopBanner, (0+260+2, 0+10)) 
        ycur = 10
        
        hour,min,sec =misctools.getTime()
        #~ hour,min = 11,28
        strTime = "%2d:%2d" % (hour,min)
        textsurface,rect = fontSysSmall.render( strTime, (0, 0, 0) )
        self.screen.blit(textsurface,(10+20+4 ,ycur+4))
        
        # title
        ycur = 28+10
        
        for i in range(3):
            y = ycur+i*6
            pg.draw.line(self.screen, colDark1,(10+6+3,y),(30+6,y),2 )

    
        #~ fontSys = pg.font.SysFont('Comic Sans MS', 30)
        #~ textsurface = fontSys.render('Faiska', False, (0, 0, 0))
        #~ fontSys = pygame.freetype.SysFont('Verdana', 18)

        #~ fontSys.underline = True
        textsurface,rect = fontSys.render('Faiska', (0, 0, 0))
        self.screen.blit(textsurface,(w//2-(rect[2]-rect[0])//2,ycur))
        ycur += 24
        
        pg.draw.line(self.screen, colLight1,(0,ycur),(w,ycur) )
        ycur += 1
        
        rTime = pg.time.get_ticks()/1000 #rTime in sec # the time of the game
        
        # screen
        # round_rect(mat,(x,y,w,h),col1,round_size,border_size)
        ycur += 20
        xmargin=20
        ymargin=20
        warea = w-xmargin*2
        harea = 500
        
        
        if self.isSpeaking():
            bWritingQuestion = pg.time.get_ticks()/1000-self.timeStartSpeak < self.rDurationSpeak
        else:
            bWritingQuestion = False
            
        xbot = xmargin+warea-self.imBot.get_rect().size[0]+xmargin//2 + 6
        ybot = ycur+harea-self.imBot.get_rect().size[1]#+ymargin//2
        
        if bWritingQuestion:
            ybot += noise.getSimplexNoise(rTime/2,100)*4
        
        rTimeBotsInOut = 2.
        if rTime < rTimeBotsInOut:
            # arrival
            xbot += 300*(rTimeBotsInOut-rTime)
        elif self.timeBotsStartExit > 0:
            xbot += 300*(rTime-self.timeBotsStartExit)/rTimeBotsInOut
        
        round_rect(self.screen, (xmargin,ycur,warea,harea), colBlue1, 10, 0)

            
        if 1:
            # draw arms
            xArm1 = xbot+8
            yArm1 = ybot+161
            
            xArm2 = xbot+173
            yArm2 = yArm1
            wArm = 18
            hArm = 140
            border_radius = 3
            
            if noise.getSimplexNoise(rTime*2) > 0.3 or 1:
                if bWritingQuestion:
                    self.rAngleArm1 = -20+ noise.getSimplexNoise((rTime)*4,20)*20
                    self.rAngleArm2 =  20 - noise.getSimplexNoise((rTime)*4,30)*20
                else:
                    self.rAngleArm1 = -2 +noise.getSimplexNoise((rTime)/3,20)*3
                    self.rAngleArm2 = -self.rAngleArm1
            rectRotated(self.screen,colBotsSkin,(int(xArm1),int(yArm1),wArm,hArm), 0, border_radius=border_radius, rotation_angle=self.rAngleArm1, rotation_offset_center=(0,-60),nAntialiasingRatio=1 )
            rectRotated(self.screen,colBlack,(int(xArm1)-1,int(yArm1)-1,wArm+1,hArm+1), 1, border_radius=border_radius, rotation_angle=self.rAngleArm1, rotation_offset_center=(0,-60),nAntialiasingRatio=4 )
            rectRotated(self.screen,colBotsSkin,(int(xArm2),int(yArm2),wArm,hArm), 0, border_radius=border_radius, rotation_angle=self.rAngleArm2, rotation_offset_center=(0,-60) )
            rectRotated(self.screen,colBlack,(int(xArm2)-1,int(yArm2)-1,wArm+1,hArm+1), 1, border_radius=border_radius, rotation_angle=self.rAngleArm2, rotation_offset_center=(0,-60),nAntialiasingRatio=4 )
          
            # test rectRotated:
            #~ rectRotated(self.screen,colBlack,(100,300,wArm+1+100,hArm+1+5), 1, border_radius=border_radius, rotation_angle=self.rAngleArm2, rotation_offset_center=(110,100),nAntialiasingRatio=4)
          
        self.screen.blit(self.imBot, (xbot, ybot))
        

        xmouth = xbot+101
        ymouth = ybot+96
        wmouth = 40
        hmouth = 30
        
        # animate bots
        
        xEye1=xbot+77
        xEye2=xbot+122
        yEye = ybot+54
        wEyeMax = 30
        hEyeMax = wEyeMax
        pg.draw.rect(self.screen,colBotsSkin,(int(xEye1-wEyeMax//2),int(yEye-hEyeMax//2),wEyeMax,hEyeMax) )
        pg.draw.rect(self.screen,colBotsSkin,(int(xEye2-wEyeMax//2),int(yEye-hEyeMax//2),wEyeMax,hEyeMax) )
        
        wEye = int( (wEyeMax+3)*(0.8+0.2*abs(noise.getSimplexNoise((rTime+10)/2))) )
        hEye = wEye
        
        if self.bInBlink:
            rTimeBlink = 0.1
            rInBlink = (rTime - self.timeStartBlink)/rTimeBlink
            if rInBlink >= 1.:
                self.bInBlink = False
            else:
                if rInBlink < 0.5:
                    hEye=int( (wEyeMax+3)*(0.5-rInBlink) )
                else:
                    hEye=int( (wEyeMax+3)*(rInBlink-0.5) )
        else:
            if random.random()>0.99:
                self.bInBlink = True
                self.timeStartBlink = rTime

        pg.draw.ellipse(self.screen,colBlack,(xEye1-wEye//2,yEye-hEye//2,wEye,hEye) )
        pg.draw.ellipse(self.screen,colBlack,(xEye2-wEye//2,yEye-hEye//2,wEye,hEye) )
        
           
        
        if self.isSpeaking() and bWritingQuestion:
            # change mouth
            pg.draw.rect(self.screen,colBotsSkin,(xmouth-wmouth//2,ymouth-hmouth//2,wmouth,hmouth) )
            
            #nMouthSize = (int(rTime)*3)%hmouth
            nMouthSize = int(abs(noise.getSimplexNoise(rTime*3))*hmouth)
            pg.draw.ellipse(self.screen,colDark1,(xmouth-nMouthSize,ymouth-nMouthSize//2,nMouthSize*2,nMouthSize) )
        
        if self.isSpeaking():
            # render question
            if self.bQuick:
                self.bQuick = False
                self.timeStartSpeak -= 5
            nEnd = int((pg.time.get_ticks()/1000-self.timeStartSpeak)*20)
            txt = self.strTxtSpeak[:nEnd]
            for i in range(nEnd,len(self.strTxtSpeak)):
                if self.strTxtSpeak[i] != ' ':
                    txt += "_"
                else:
                    txt += " "
            renderTxtMultiline( self.screen, txt, (xmargin*2,ycur+ymargin-5),fontTxt, colDark1,nWidthMax=300)
            ycur += harea+10
        
            # microphone over mouth
            wmicro = 26
            hmicro = 16
            pg.draw.ellipse(self.screen,colBotsMicro,(xmouth-wmicro//2-26,ymouth-hmicro//2+2,wmicro,hmicro) )

            if nEnd >= len(self.strTxtSpeak):
                self.renderUserButton( self.screen,(xmargin,ycur) )

        
        ycur=670
        
        # progression
        round_rect(self.screen, (xmargin,ycur,warea,20), colLight1, 2, 0)
        rProgress = (self.nNumQ) / len(self.listQ)
        if rProgress > 1.: rProgress = 1.
        if rProgress > 0.1:
            round_rect(self.screen, (xmargin,ycur,int(warea*rProgress),20), colBlue1, 2, 0)
            
        if rProgress == 1.:
            if self.timeBotsStartExit == 0:
                self.timeBotsStartExit = rTime
        
    # draw - end


    def main_loop(self):
        random.seed(1000) # tune to have a blink during the first question
        self.listQ = []
        #~ self.listQ.append(["C?", ["Oui", "bof", "Non", "car","or"]])
        #~ self.listQ.append(["Comparé à votre précédente mission chez Sephora, celle ci vous a t'elle paru plus agréable?", ["Oui", "Bof", "Non"]])
        #~ self.listQ.append(["Super, et quel aspect vous a le plus plu?", ["Le\ncadre", "Les\ncollégues", "Le\nmanager", "un\npeu\ntout"]])
        #~ self.listQ.append(["J'ai adoré discuter avec vous!",["Moi\naussi!", "C'étais\npas mal.", "Moi\npas trop..."]] )
        #~ self.listQ.append(["Merci et à bientot!",["De rien, au revoir!", "Bye!"]] )
        #~ self.listQ.append(["Merci à bientot!",["De rien, au revoir! Grave de la grosse balle atomiaque de gros malade!", "Bye!"]] )
        self.listQ.append(["Comment avez-vous pris connaissance de cette offre d’emploi ?",["sur notre site internet", "sur un jobboard", "par le bouche à oreille"]] )
        self.listQ.append(["Quel est le niveau de votre rémunération actuelle ?",["de 20000 à 30000€ brut annuel", "de 30000 à 40000€", "plus de 50000€"]] )
        self.listQ.append(["Combien de temps vous faut il pour rejoindre le lieu de travail ?",["jusqu’à 30min", "de 30 à 45min", "plus de 45min"]] )
        self.listQ.append(["Quel est votre niveau d’anglais ?",["bilingual", "professional", "average"]] )
        self.listQ.append(["Combien d’années d’expérience avez-vous à ce poste ?",["Moins de 2 ans", "entre 2 et 4", "5 ans et plus"]] )
        self.listQ.append(["Combien d’années d’études post bac ?",["0", "2", "4 et plus"]] )
        #~ self.listQ.append(["?",["", "", ""]] )
        
        
        self.nNumQ = 0
        #~ self.nNumQ = 1;self.listQ[self.nNumQ][0]="C"
        #~ print(listQ)
        
        nCpt = 0
        timeFps = time.time()
        nCptImageTotal = 0
        while not self.done:
            self.event_loop()
            rTime = pg.time.get_ticks()/1000
            nTime = int(rTime)
            if rTime >= 4. and not self.isSpeaking():
                #~ self.speak()
                #~ self.nNumQ += 1
                if self.nNumQ < len(self.listQ):
                    self.speak( self.listQ[self.nNumQ][0],self.listQ[self.nNumQ][1])
                    #~ self.speak("C?", ["Oui", "bof", "Non", "car","or"])
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            nCpt += 1
            if nCpt > 200:
                duration = time.time() - timeFps
                print("INF: fps: %5.1f" % (nCpt/duration) )
                nCpt = 0
                timeFps = time.time()
                
                    
            nCptImageTotal += 1
            if 0: # if (nCptImageTotal % (500*1000)) == 0 or 1:
                #ffmpeg -r 10 -i %d.png -vcodec libx264 -b:v 4M -an test.mp4 # -an: no audio
                #ffmpeg -r 60 -i "%d.png" -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 123 output.gif
                filename = "d:/images_generated/" + str(nCptImageTotal) + ".png"
                pygame.image.save(self.screen, filename)
                
                

#class Agent - end

def runAgent():
    a = Agent((700//2,720))
    a.main_loop()
    pg.quit()
    
if __name__ == "__main__":
    runAgent()
    sys.exit()