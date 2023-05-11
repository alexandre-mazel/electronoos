import math
import pygame as pg
import random

successes, failures = pg.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
yellowd = (230, 230, 0)
orange = (255, 135, 0)
blue = (0, 0, 255)
bluel = (127, 127, 255)


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


class Player:
    def __init__(self,x=200,y=200,r=10,angle=0):
        self.x = x
        self.y = y
        self.r = r
        self.vx = 0
        self.vy = 0
        self.bAccelerate = False

        self.angle = angle
        self.lifemax = 100
        self.life = self.lifemax
    
    def update(self,ws,hs):
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
        # impossible to apply that, because we don't have inertia in our ship
        self.vx += 0.3*math.cos(projectile_angle)
        self.vy += 0.3*math.sin(projectile_angle)

    
    def render(self, surface):
        color = bluel
        pg.draw.circle(surface,color,(self.x,self.y),self.r,width=2)
        x2 = self.x+math.cos(self.angle)*(self.r+5)
        y2 = self.y+math.sin(self.angle)*(self.r+5)
        pg.draw.line(surface,color,(self.x,self.y),(x2,y2),width=1)
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
        
        if self.bAccelerate:
            x1 = self.x-math.cos(self.angle)*(self.r-1)
            y1 = self.y-math.sin(self.angle)*(self.r-1)
            x2 = self.x-math.cos(self.angle)*(self.r+4)
            y2 = self.y-math.sin(self.angle)*(self.r+4)
            pg.draw.line(surface,orange,(x1,y1),(x2,y2),width=7)
            
            self.bAccelerate = False
        
    def shoot(self):
        """
        create a projectile coming from me.
        return the created projectile
        """
        vproj = (abs(self.vx)+abs(self.vx))*1.1+1
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

        return self.life > 0
    
    def render(self, surface):
        color = red
        pg.draw.circle(surface,color,(self.x,self.y),2,width=2)
        
        
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
        self.screen = pg.display.set_mode((1024, 768))
        self.ws = self.screen.get_width()
        self.hs = self.screen.get_height()
        
        self.clock = pg.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.players = []
        self.players.append(Player())
        self.players.append(Player(x=self.ws-200,angle=math.pi))
        
        self.projectiles = []
        self.planets = []
        
        
        
        for i in range(4):
            self.planets.append(Planet())

        
        self.keypressed={} # will store current keyboard pressed
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
                
            if event.type == pg.KEYDOWN:     
                #~ print("DBG: key '%s' pressed" % event.key )
                self.keypressed[event.key] = 1
                
            if event.type == pg.KEYUP:
                self.keypressed[event.key] = 0
                
                if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                    self.addProjectile(0)
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                if key == pg.K_a or key == pg.K_UP:
                    self.players[0].vx += 0.05*math.cos(self.players[0].angle)
                    self.players[0].vy += 0.05*math.sin(self.players[0].angle)
                    self.players[0].bAccelerate = True
                elif key == pg.K_q or key == pg.K_DOWN:
                    self.players[0].vx -= 0.05*math.cos(self.players[0].angle)
                    self.players[0].vy -= 0.05*math.sin(self.players[0].angle)
                elif key == pg.K_q or key == pg.K_LEFT:
                    self.players[0].angle -= 0.05
                elif key == pg.K_q or key == pg.K_RIGHT:
                    self.players[0].angle += 0.05
                elif key == pg.K_ESCAPE:
                    return True
                    
                self.players[0].vx = limit(self.players[0].vx,3)
                self.players[0].vy = limit(self.players[0].vy,3)
                    
        return False
        
    def addProjectile(self, numPlayer):
        newProj = self.players[numPlayer].shoot()
        self.projectiles.append(newProj)
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        for p in self.planets:
            p.update(self.ws,self.hs)
        
        for p in self.players:
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
                    p.vx = -p.vx*0.7
                    p.vy = -p.vy*0.7
                

        i = 0
        while i < len(self.projectiles):
            if not self.projectiles[i].update(self.ws,self.hs):
                del self.projectiles[i]
                continue
            i += 1
            
            
        for proj in self.projectiles:
            
            # colliding with everything
            
            for p in self.players+self.planets :                
                if distSquared(proj,p)<p.r*p.r:
                    # touch
                    damage = 10*abs(proj.v)
                    damage = 1
                    if isinstance(p,Player):
                        p.receiveDamage(damage, proj.v,proj.angle)
                    # rebond direct (prevent further touch)
                    proj.x -= math.cos(proj.angle)*proj.v
                    proj.y -= math.sin(proj.angle)*proj.v
                    proj.angle += 180 + (random.random()*2)-1
                
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)

        for p in self.planets:
            p.render(self.screen)
            
        for p in self.players:
            p.render(self.screen)
            
        for p in self.projectiles:
            p.render(self.screen)
            
        pg.display.update()  # or pygame.display.flip()
        
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


runGame()