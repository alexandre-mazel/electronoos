import math
import pygame as pg
import random
import time

successes, failures = pg.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
gray = (127, 127, 127)
white = (255, 255, 255)
red = (255, 0, 0)
pink = (255, 127, 127)
green = (0, 255, 0)
greenl = (127, 255, 127)
yellow = (255, 255, 0)
yellowd = (230, 230, 0)
orange = (255, 135, 0)
blue = (0, 0, 255)
bluel = (127, 127, 255)

def blendColor(color,alpha,backColor = (0,0,0)):
    """
    Dim a color (make it blend with background)
    - alpha: 0: totally transparent, 1: opaque
    """
    return int(color[0]*alpha+backColor[0]*(1-alpha)),int(color[1]*alpha+backColor[1]*(1-alpha)),int(color[2]*alpha+backColor[2]*(1-alpha))
    

"""
Exemple de collision entre 2 rectangles
"""
def isIntersectedSegments(x1,len1,x2,len2):
    """
    is there an intersection between segment starting at x1 of len1 and segment starting at x2 of len2
    """
    
    return not(x1+len1<x2 or x1>x2+len2)
    
"""
isCollision = isIntersectedSegments(square.x, square.w, obstacle.x, obstactle.w)  \
                        and isIntersectedSegments(square.y, square.h, obstacle.y, obstactle.h)
    if bIsCollision:
        # reaction a la collision
        print("collision square obstacle")
        square.vx *= -1
        # blablabla
"""

def distSquared(a,b):
    return (a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y)
    
def limit(val,maxval):
    """
    ensure val is in [-maxval,maxval]
    """
    if abs(val)<=maxval:
        return val
    if val < 0:
        return -maxval
    return maxval

def norm2pi(a):
    if a<0: a+=math.pi*2
    elif a > math.pi*2: a-=math.pi*2
    return a
    
def normpi(a):
    print("DBG:normpi (1): %s" % a)
    if a < -math.pi: a+=math.pi*2
    elif a > math.pi: a-=math.pi*2
    print("DBG:normpi (2): %s" % a)
    return a
    
class Effect:
    def __init__(self,x,y,text="",color=white):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifemax = 60
        self.life = self.lifemax
        self.size = 24
        self.fontTitle = pg.font.SysFont('Arial', self.size)
        
    def update(self):
        self.life -= 1
        nPrevSize = self.size
        self.size = self.life
        self.y -= 3
        #~ self.x -= (self.life%7)-3
        if self.size != nPrevSize and 0:
            self.fontTitle = pg.font.SysFont('Arial', self.size)
            
        return self.life>0
        
    def render(self, surface):
        color = blendColor(self.color,min(1,self.life/(self.lifemax//3)))
        text_surface = self.fontTitle.render(self.text, False, color)
        surface.blit(text_surface, (self.x,self.y))
        
# class Effect - end        
    

class Player:
    def __init__(self,x=200,y=200,r=10,angle=0,color=bluel):
        self.x = x
        self.y = y
        self.r = r
        self.vx = 0
        self.vy = 0

        self.angle = angle
        self.lifemax = 10
        self.life = self.lifemax
        self.bDead = 0
        self.color = color
        self.bAccelerating = False
        self.timeFrozen = time.time()
        
        self.bMulti = 0
        self.bExplode = 0
        self.bDiaree = 0
    
    def update(self,ws,hs):
        if time.time() > self.timeFrozen:
            self.x += self.vx
            self.y += self.vy
        
        rCoefFrot = 0.995
        self.vx *= rCoefFrot
        self.vy *= rCoefFrot
        
        # warping
        if self.x>ws:
            self.x-=ws
        elif self.x<0:
            self.x+=ws
            
        if self.y>hs:
            self.y-=hs
        elif self.y<0:
            self.y+=hs
            
    def receiveDamage( self, damage, projectile_speed,projectile_angle):
        self.life -= damage
        self.vx += 0.3*math.cos(projectile_angle)
        self.vy += 0.3*math.sin(projectile_angle)

    
    def render(self, surface):
        color = self.color
        if self.bDead:
            color = gray
        pg.draw.circle(surface,color,(self.x,self.y),self.r,width=2)
        x2 = self.x+math.cos(self.angle)*(self.r+5)
        y2 = self.y+math.sin(self.angle)*(self.r+5)
        pg.draw.line(surface,color,(self.x,self.y),(x2,y2),width=1)
        
        if not self.bDead:
            # life bar
            barw2 = 30
            barh2 = 4
            barcolor = green
            if self.life <= self.lifemax*0.7:
                barcolor = yellowd
            if self.life <= self.lifemax*0.35:
                barcolor = red
            pg.draw.rect(surface,white,(self.x-barw2,self.y+self.r+12-barh2,barw2*2,barh2*2))
            pg.draw.rect(surface,barcolor,(self.x-barw2+2,self.y+self.r+12-barh2+2,(barw2*2-4)*(self.life/self.lifemax),barh2*2-4))
        
        if self.bAccelerating:
            x1 = self.x-math.cos(self.angle)*(self.r-1)
            y1 = self.y-math.sin(self.angle)*(self.r-1)
            x2 = self.x-math.cos(self.angle)*(self.r+4)
            y2 = self.y-math.sin(self.angle)*(self.r+4)
            pg.draw.line(surface,orange,(x1,y1),(x2,y2),width=7)
            
            self.bAccelerating = False
        
    def shoot(self):
        """
        create a projectile coming from me.
        return the created projectile
        """
        vproj = (abs(self.vx)+abs(self.vy))*1.1+1
        p = Projectile(self.x+math.cos(self.angle)*(self.r+5),self.y+math.sin(self.angle)*(self.r+5),vproj,self.angle)
        return p

# class Player - end

class Projectile:
    def __init__(self,x=100,y=100,v=0,angle=0):
        self.x = x
        self.y = y
        self.v = v
        self.angle = angle
        self.life = 800
        self.color = red
        self.bExplode = 0
    
    def update(self,ws,hs):
        """
        return false if this projectile is dead
        """
        self.x += math.cos(self.angle)*self.v
        self.y += math.sin(self.angle)*self.v
        
        # warping
        if self.x>ws:
            self.x-=ws
        elif self.x<0:
            self.x+=ws
            
        if self.y>hs:
            self.y-=hs
        elif self.y<0:
            self.y+=hs
            
        self.life -= 1
        
        if self.life <= 700 and self.bExplode:
            self.life = 0
            global global_theGame
            rAngleInc = 0.1
            n = 63
            color = [pink,red,blue,green,yellow][random.randint(0,4)]
            for i in range(n):
                newProj = Projectile()
                newProj.angle += rAngleInc*(i-n//2)
                newProj.x = self.x
                newProj.y = self.y
                newProj.v = 1+random.random()*0.1
                newProj.life //= 4
                newProj.color = color
                global_theGame.projectiles.append(newProj)      

        return self.life > 0
    
    def render(self, surface):
        pg.draw.circle(surface,self.color,(self.x,self.y),2,width=2)
        
        
class Bonus:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = 30
        self.h = 30
        #~ self.v = v
        #~ self.angle = angle
        self.ttl = 1000
        self.color = white
        self.fontTitle = pg.font.SysFont('Arial', 24)
        self.text_surface = self.fontTitle.render('?', False, self.color)
    
    def update(self,ws,hs):
        """
        return false if this object is dead
        """
        self.ttl -= 1
        return self.ttl > 0
            
    
    def render(self, surface):
        
        color = self.color
        pos = [self.x,self.y,self.w,self.h]
        pg.draw.rect(surface,color,pos,width=2)
        
        surface.blit(self.text_surface, (pos[0]+self.w//3+1,pos[1]))       
        
        # 2 squares in corner
        nSizeCorner = 8
        pos[2] = nSizeCorner
        pos[3] = nSizeCorner
        
        pos[0] = self.x+self.w-nSizeCorner
        pg.draw.rect(surface,color,pos,width=2)
        pos[0] = self.x
        pos[1] = self.y+self.h-nSizeCorner
        pg.draw.rect(surface,color,pos,width=2)
        
        

        
        
class Planet:
    def __init__(self,x=0,y=0,r=50,angle=0):
        self.x = x
        self.y = y
        self.r = random.randint(50,200)
        self.vx = random.random()*2-1
        self.vy = random.random()*2-1
        self.color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
        
    def update(self,ws,hs):
        self.x += self.vx
        self.y += self.vy
        
        # warping
        if self.x>ws:
            self.x-=ws
        elif self.x<0:
            self.x+=ws
            
        if self.y>hs:
            self.y-=hs
        elif self.y<0:
            self.y+=hs
        
    def render(self, surface):
        pg.draw.circle(surface,self.color,(self.x,self.y),self.r,width=0)
        

class Game:
    def __init__(self):
        w = 1380
        h = 920
        if 0:
            # reduce screen to see debug
            w = 640
            h = 480
        self.screen = pg.display.set_mode((w,h))
        self.ws = self.screen.get_width()
        self.hs = self.screen.get_height()
        
        self.clock = pg.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.projectiles = []
        self.planets = []
        self.bonuses = []
        self.effects = []
        
        self.bOpponentIsAi = 1 # turn to one to activate AI
        self.bOpponentIsAi = 0
        
        pg.font.init() # you have to call this at the start, 
                   # if you want to use this module.
        self.fontTitle = pg.font.SysFont('Comic Sans MS', 30)

        
        
        
        #~ for i in range(4):
            #~ self.planets.append(Planet())

        
        self.keypressed={} # will store current keyboard pressed
        
        self.loadSound()
        
        self.startNewGame()
        
        self.score = [0]*len(self.players)
        
    def loadSound(self):
        self.sound_missile = pg.mixer.Sound("weird_laser.wav")
        self.sound_crash = pg.mixer.Sound("crash.wav")
        
    def startNewGame(self):
        self.players = []
        self.players.append(Player(x=self.ws-200,angle=math.pi))
        self.players.append(Player(color=greenl))
        #~ self.players.append(Player(x=self.ws/2,y=600, angle=-math.pi/2,color=yellow))
        self.nNumPlayerRemaining = len(self.players)
        
        self.bEndOfGame = 0
        
        #~ self.players[0].bMulti = 1
        #~ self.players[0].life *= 5
        
        self.effects.append(Effect(self.ws//2,self.hs//2,"Let's Fight !!!"))
        
        
    def getCommandAI(self):
        
        nFront = nTurn = bShoot = 0
        
        playerAi = self.players[1]
        
        #
        # dodge missile
        #
        
        # find nearest one
        nDistNearest = 9999*9999
        projNearest = None
        for proj in self.projectiles:
            d = distSquared(proj,playerAi)
            if d < nDistNearest:
                nDistNearest = d
                projNearest = proj
                
        if nDistNearest < 16000:
            print("DBG: getCommandAI: proj near!")
            
            dx = projNearest.x - playerAi.x
            dy = projNearest.y - playerAi.y
            dangle = normpi(math.atan2(dy,dx))
            diffangle = dangle-playerAi.angle
            print("DBG: getCommandAI: diffangle: %.3f, dist: %s" % (diffangle,nDistNearest) )
            
            # near and facing => rear
            if abs(diffangle) < 0.2 and nDistNearest < 8000:
                nFront = -1
            else:
                # change dir then accelerate
                if 0 <= diffangle < 1.:
                    nTurn = 1
                elif 0 > diffangle > -1:
                    nTurn = -1
                else:
                    nFront = 1
                
            # freine ?
            #~ if nTurn != 0:
                #~ if playerAi.vx > 0:
                    #~ nFront = -1

        else:
            #
            #  chase other
            #
            dx = self.players[0].x-playerAi.x
            dy = self.players[0].y-playerAi.y
            dist = dx*dx+dy*dy
            #~ print("dist: %s" % dist )
            if dist < 80000:
                if random.random()>0.95:
                    print("shoot")
                    bShoot = 1
            else:
                nFront=1
            
            
            dangle = norm2pi(math.atan2(dy,dx))
            #~ print("dangle: %.2f" % dangle)
            diffangle = dangle-playerAi.angle
            print("dangle: %.2f, angle:%.2f, diff: %.2f" % (dangle,playerAi.angle,diffangle))
            if diffangle < -0.05:
                nTurn = 1
                nFront = 0
            elif diffangle > 0.05:
                nTurn = -1
                nFront = 0
            #~ elif math.atan2(dy,dx)-playerAi.angle<-0.1
                #~ nTurn=-1
                
        return nFront,nTurn,bShoot
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        # define keys for each player
        
        listConfigKeys = [
                            # accelerate, decelerate, left, right, shoot
                            [pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT,pg.K_EXCLAIM], # player 1  # pg.K_SPACE
                            [pg.K_z,pg.K_s,pg.K_q,pg.K_d,pg.K_a], # player 2
                            [pg.K_g,pg.K_b,pg.K_v,pg.K_n,pg.K_f], # player 3
                      ]
                      
                      
        if self.bOpponentIsAi:
            if not self.bEndOfGame:
                # AI emulate keys:
                # to rewrite: badly programmed
                nFrontAI, nTurnAI,bShootAI = self.getCommandAI()
                #~ print("nFrontAI, nTurnAI,bShootAI: %s,%s,%s" % (nFrontAI, nTurnAI,bShootAI) )
                self.keypressed[listConfigKeys[1][0]] = 0
                self.keypressed[listConfigKeys[1][1]] = 0
                if nFrontAI == 1: self.keypressed[listConfigKeys[1][0]] = 1
                elif nFrontAI == -1: self.keypressed[listConfigKeys[1][1]] = 1

                self.keypressed[listConfigKeys[1][2]] = 0
                self.keypressed[listConfigKeys[1][3]] = 0
                    
                if nTurnAI == 1: self.keypressed[listConfigKeys[1][2]] = 1
                elif nTurnAI == -1: self.keypressed[listConfigKeys[1][3]] = 1

                
                if bShootAI == 1: 
                    # ugly: cut and paste! don't do that please
                    self.addProjectile(1)
                    pg.mixer.Sound.play(self.sound_missile)
                    
                      
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
                
            if event.type == pg.KEYDOWN:     
                #~ print("DBG: key '%s' pressed" % event.key )
                self.keypressed[event.key] = 1
                                    
                for numplayer,configkey in enumerate(listConfigKeys):
                    if numplayer >= len(self.players):
                        break
                        
                    if self.players[numplayer].bDead:
                        continue
                    key_shoot = configkey[4]
                    if event.key == key_shoot:
                        self.addProjectile(numplayer)
                        pg.mixer.Sound.play(self.sound_missile)
                
            if event.type == pg.KEYUP:
                self.keypressed[event.key] = 0


        for key, bPressed in self.keypressed.items():
            if bPressed:
                for numplayer,configkey in enumerate(listConfigKeys):
                    key_up, key_down, key_left, key_right, key_shoot = configkey
                    if key == key_up:
                        self.players[numplayer].vx += 0.05*math.cos(self.players[numplayer].angle)
                        self.players[numplayer].vy += 0.05*math.sin(self.players[numplayer].angle)
                        self.players[numplayer].bAccelerating = True
                    elif key == key_down:
                        self.players[numplayer].vx -= 0.05*math.cos(self.players[numplayer].angle)
                        self.players[numplayer].vy -= 0.05*math.sin(self.players[numplayer].angle)
                    elif key == key_left:
                        self.players[numplayer].angle -= 0.05
                    elif key == key_right:
                        self.players[numplayer].angle += 0.05
                
                if key == pg.K_ESCAPE:
                    return True
                    
                self.players[0].vx = limit(self.players[0].vx,3)
                self.players[0].vy = limit(self.players[0].vy,3)
                    
        return False
        
    def addProjectile(self, numPlayer):
        newProj = self.players[numPlayer].shoot()
        newProj.bExplode = self.players[numPlayer].bExplode
        self.projectiles.append(newProj)
        if self.players[numPlayer].bMulti and 1:
            rAngleInc = 0.1
            for i in range(5):
                newProj = self.players[numPlayer].shoot()
                newProj.bExplode = self.players[numPlayer].bExplode
                newProj.angle += rAngleInc*(i-2)
                self.projectiles.append(newProj)         
                
        #~ self.projectiles = self.projectiles[-1000:]

            
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        if self.bEndOfGame:
            return
        
        for p in self.planets:
            p.update(self.ws,self.hs)
            
        i = 0
        while i < len(self.effects):
            if not self.effects[i].update():
                del self.effects[i]
                continue
            i += 1
        
        for num_player,p in enumerate(self.players):
            if p.bDiaree and int(time.time()) % 6 == 0 and self.clock.get_fps() > 30:
                self.addProjectile(num_player)
            p.update(self.ws,self.hs)

            
        # collision interplayer
        for i in range(len(self.players)):
            for j in range(i,len(self.players)):
                if i == j:
                    continue
                if distSquared(self.players[i],self.players[j])<math.pow(self.players[i].r,2)+math.pow(self.players[j].r,2):
                    ovx = self.players[j].vx
                    ovy = self.players[j].vy
                    self.players[j].vx = self.players[i].vx * 0.7 - self.players[j].vx * 0.7
                    self.players[j].vy = self.players[i].vy * 0.7 - self.players[j].vy * 0.7
                    self.players[i].vx = -self.players[i].vx * 0.7 + ovx * 0.7
                    self.players[i].vy = -self.players[i].vy * 0.7 + ovy * 0.7     
                    self.players[i].life -= 2             
                    self.players[j].life -= 2             

        # collision player /planets
        for p in self.players:
            for planet in self.planets:
                if distSquared(p,planet)<math.pow(p.r,2)+math.pow(planet.r,2):
                    
                    sumv = abs(p.vx)+abs(p.vy)
                    if sumv>1.5:
                        #~ self.sound_crash.set_volume(sumv/2)
                        pg.mixer.Sound.play(self.sound_crash)
                        
                    
                    p.vx = -p.vx*0.7 + planet.vx
                    p.vy = -p.vy*0.7 + planet.vy
                    
                    if abs(p.vx) < 0.01 and abs(p.vy) < 0.01:
                        p.vx = planet.vx+(random.random()*2-1)*0.1
                        p.vy = planet.vy+(random.random()*2-1)*0.1
                    cpt = 1
                    while distSquared(p,planet)<math.pow(p.r,2)+math.pow(planet.r,2):
                        # move point while into object
                        p.x += p.vx
                        p.y += p.vy
                        #~ print("x: %s, y: %s vx: %s, vy: %s" % (p.x,p.y,p.vx,p.vy))
                        cpt+= 1
                        if cpt > 100:
                            break
                            
                            
                            
        # collision player / bonuses
        for p in self.players:
            for b in self.bonuses:
                if distSquared(p,b)<math.pow(p.r,2)+math.pow(b.w,2):
                    txt = ""
                    color = green
                    b.ttl = 0
                    if random.random() > 0.5:
                        if random.random() > 0.5 and not p.bMulti:
                            p.bMulti = 1
                            txt = "multi"
                        elif random.random() > 0.5 and not p.bExplode:
                            p.bExplode = 1
                            txt = "explode"
                        else:
                            p.life += 3
                            if p.life>p.lifemax:
                                p.life = p.lifemax
                            txt = "life up"
                    else:
                        p.timeFrozen = time.time()+5.
                        p.vx = 0
                        p.vy = 0
                        txt = "frozen"
                        color = red
                        
                    self.effects.append(Effect(p.x-20,p.y,txt,color))
                

        i = 0
        while i < len(self.projectiles):
            if not self.projectiles[i].update(self.ws,self.hs):
                del self.projectiles[i]
                continue
            i += 1
            
        i = 0
        while i < len(self.bonuses):
            if not self.bonuses[i].update(self.ws,self.hs):
                del self.bonuses[i]
                continue
            i += 1
            
        if random.random()>0.995:
            b = Bonus(random.randint(0,self.ws-1),random.randint(0,self.hs-1))
            self.bonuses.append(b)
            
            
        for proj in self.projectiles:
            
            # colliding with everything
            
            for p in self.players+self.planets :                
                if distSquared(proj,p)<p.r*p.r:
                    # touch
                    damage = 10*abs(proj.v)
                    damage = 1
                    if isinstance(p,Player):
                        p.receiveDamage(damage, proj.v,proj.angle)

                    pg.mixer.Sound.play(self.sound_crash)
                    
                    while distSquared(proj,p)<p.r*p.r:
                        # move point while into object
                        proj.x -= math.cos(proj.angle)*proj.v
                        proj.y -= math.sin(proj.angle)*proj.v
                    proj.angle += 180 + (random.random()*2)-1
                    
                    
        nCountRemaining = 0
        for num_player,p in enumerate(self.players):
            if p.bDead:
                continue
            if p.life <= 0:
                print("player %d lose" % num_player)
                #~ self.bEndOfGame = 1
                p.bDead = 1
                self.nNumPlayerRemaining -= 1
                if self.nNumPlayerRemaining == 1:
                    self.bEndOfGame = 1
                    self.timeRestartGame = time.time()+5
                    
                    # find winner number
                    for num_player,p in enumerate(self.players):
                        if not p.bDead:
                            break
                    self.score[num_player] += 1
                    
                        
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)

        for p in self.planets:
            p.render(self.screen)
            
        for p in self.bonuses:
            p.render(self.screen)
            
        for p in self.effects:
            p.render(self.screen)
            
        for p in self.players:
            p.render(self.screen)

            
        for p in self.projectiles:
            p.render(self.screen)
            
        if self.bEndOfGame:
            color = white
            rectMessage = (100,100,self.ws-200,self.hs-400)
            pg.draw.rect(self.screen,color,rectMessage,width=10)
            text_surface = self.fontTitle.render('Game Over', False, color)
            self.screen.blit(text_surface, (rectMessage[0]+320,rectMessage[1]+100))
            
            # find winner number
            for num_player,p in enumerate(self.players):
                if not p.bDead:
                    break

            color = self.players[num_player].color
            text_surface = self.fontTitle.render('Player %d is the winner' % (num_player+1), False, color)
            self.screen.blit(text_surface, (rectMessage[0]+300,rectMessage[1]+200))
            
            offsety = 0
            for num_player,p in enumerate(self.players):
                color = p.color
                text_surface = self.fontTitle.render('Player %d: %d' % (num_player+1,self.score[num_player]), False, color)
                self.screen.blit(text_surface, (rectMessage[0]+300,rectMessage[1]+260+offsety))         
                offsety += 30
                
            if time.time() > self.timeRestartGame:
                self.startNewGame()
                
        pg.display.update()  # or .display.flip()
        
        
# class Game - end


global_theGame = None
def runGame():
    global global_theGame
    game = Game()
    global_theGame = game
    while 1:
        bQuit = game.handleInput()
        if bQuit:
            break
        game.update()
        game.render()
        
# startGame - end


runGame()

"""
terminal:
faire des tps sur 1 mois (sur une notion specifique?)
puis 3 dernier mois un gros projets.

premiere:
la partie sur les classe va trop vite
plusse de  cours
"""

