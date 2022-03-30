import math
import pygame
import random

import sys
sys.path.append("../alex_pytools")
import csv_loader


todo: faire une méthode qui trace un blob qui doit englober n point., avec un super effet joli
zone d'influence, ou niveau d'altitude...

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)

listColor = [
                    (0, 0, 255),
                    (0, 255, 0),
                    (255, 0, 0),
                    
                    (127, 0, 127),
                    (0, 127, 127),
                    (127, 0, 127),
                    
                    (127, 127, 255),
                    (64, 255, 127),
                    (255, 127, 255),
            ]

font = pygame.font.Font('freesansbold.ttf', 24)

def dist2D2(a,b):
    return (a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1])
    
def warp(x,max):
    if x < 0:
        return max-1
    if x >= max:
        return 0
    return x
    
def crop(x,max):
    if x < 0:
        return 0
    if x >= max:
        return max-1
    return x
    
def getCommon(list1,list2):
    """
    return nbr of common element both lists
    """
    n = 0
    for l in list1:
        if l in list2:
            n+=1
    return n
    
class Sphere:
    def __init__( self, nTheme ):
        self.zone_size = 128
        sx = self.zone_size
        sy = self.zone_size
        self.zone = pygame.Surface((sx,sy), pygame.SRCALPHA)
        #~ self.zone.fill((255,255,255,128))
        color = listColor[nTheme%len(listColor)]
        for j in range(sy):
            for i in range(sy):
                a = 4*int(64-math.sqrt(dist2D2((i,j),(sx//2,sy//2))))
                a = crop(a,255)
                self.zone.set_at((i,j), (color[0],color[1],color[2],a) )
                
    def render(self, screen, pos ):
        screen.blit(self.zone, [pos[0]-self.zone_size//2+20,pos[1]-self.zone_size//2+10])

aSphereByTheme = [] # 0 => theme1, 1=> theme2...

class Agent:
    def __init__( self, strName, nTheme, size_world ):
        print("DBG: Agent: creating '%s' theme %d" % (strName, nTheme) )
        self.strName = strName
        self.anTheme = [nTheme]
        self.pos = [ random.randint(0,size_world[0]-1),random.randint(0,size_world[1]-1) ]

        self.text_img = font.render(strName, True, white)
        #~ self.text_img = font.render(str(nTheme), True, green, blue) # for debug
        #~ self.text_img = font.render(str(nTheme), True, white) # for debug
 
        self.text_rect = self.text_img.get_rect()
        self.text_rect.center = self.pos
        
        self.zone = Sphere(nTheme) # unused
                
    def addTheme(self,nTheme):
        self.anTheme.append(nTheme)

    def update( self ):
        self.text_rect.center = [int(self.pos[0]),int(self.pos[1])]
        
    def render( self, screen ):
        #~ screen.blit(self.zone, [self.text_rect[0]-self.zone_size//2+20,self.text_rect[1]-self.zone_size//2+10])
        #~ self.zone.render(screen,self.text_rect)
        for n in self.anTheme:
            aSphereByTheme[n-1].render(screen,self.text_rect)
        screen.blit(self.text_img, self.text_rect)

        
class Game:
    def __init__(self):
        self.size_world = (1200, 800)
        self.screen = pygame.display.set_mode(self.size_world)
        self.clock = pygame.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.square_img = pygame.Surface((32, 32))
        self.square_img.fill(white)
        self.square_pos = [0,0]
        
        # load agents
        self.agents = []
        data = csv_loader.load_csv("Venn-Tadiello_Data2.csv",sepa=',', bVerbose=1)
        print(data)
        for line in data[1:]:
            for idx, word in enumerate(line):
                if len(word)>1:
                    nTheme = idx+1
                    #~ self.agents.append(Agent(word,nTheme,self.size_world))
                    for i in range(len(self.agents)):
                        if self.agents[i].strName == word:
                            self.agents[i].addTheme(nTheme)
                            break
                    else:
                        self.agents.append(Agent(word,nTheme,self.size_world))
                        
        nbrTheme = 9
        for n in range(nbrTheme):
            aSphereByTheme.append( Sphere(n) )
    
    def update(self):
        self.clock.tick(self.fps)
        
        #~ self.square_pos[0] += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # explode
                    maxr  = self.size_world[0]//20
                    for i in range(len(self.agents)):
                        self.agents[i].pos[0] += random.randint(0,maxr)-maxr//2
                        self.agents[i].pos[1] += random.randint(0,maxr)-maxr//2
                    

            
        for i in range(len(self.agents)):
            rDistMin = 5555
            jmin = -1
            for j in range(len(self.agents)):
                if i == j:
                    continue
                rDist = dist2D2(self.agents[i].pos, self.agents[j].pos)
                if rDist < rDistMin:
                    rDistMin = rDist
                    jmin = j
            # j is nearest:
            j = jmin
            #~ if self.agents[i].nTheme == self.agents[j].nTheme and rDistMin > 200:
            nDistLimit = 4000 # squared dist
            if getCommon(self.agents[i].anTheme,self.agents[j].anTheme) > 1 and rDistMin > nDistLimit:
                # attract
                rCoef = 0.5
                
                if rDistMin > nDistLimit*1.1:
                    x = self.agents[i].pos[0]*(1-rCoef) + self.agents[j].pos[0]*(rCoef)
                    y = self.agents[i].pos[1]*(1-rCoef) + self.agents[j].pos[1]*(rCoef)
                    
                    #~ if isEmpty(x,y):
                    if 1:
                        self.agents[i].pos[0] = x
                        self.agents[i].pos[1] = y
                    
            else:
                #repulse
                if random.random()>0.7:
                    if self.agents[j].pos[0] > self.agents[i].pos[0]:
                        self.agents[i].pos[0] -= 1
                    else:
                        self.agents[i].pos[0] += 1
                   
                if random.random()>0.7:
                    if self.agents[j].pos[1] > self.agents[i].pos[1]:
                        self.agents[i].pos[1] -= 1
                    else:
                        self.agents[i].pos[1] += 1

                self.agents[i].pos[0] = warp(self.agents[i].pos[0],self.size_world[0])
                self.agents[i].pos[1] = warp(self.agents[i].pos[1],self.size_world[1])

                
            #~ break
                
        for a in self.agents:
            a.update()          
                    
        return False

    def render(self):
        self.screen.fill(black)
        
        #~ self.screen.blit(self.square_img, [self.square_pos[0],self.square_pos[1],self.square_pos[0]+32,self.square_pos[1]+32] )
        
        for a in self.agents:
            a.render(self.screen)
            
        pygame.display.update()  # Or pygame.display.flip()
        
# class Game - end

def startGame():
    game = Game()
    cpt = 0
    while 1:
        bQuit = game.update()
        if bQuit:
            break
        if cpt % 10 == 0 or 1:
            game.render()
        cpt += 1
        
# startGame - end

startGame()