import math
import pygame
import pygame as pg

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)
lblue = (127, 127, 255)



class Player:
    def __init__(self,x=100,y=100,r=10,angle=0):
        self.x = x
        self.y = y
        self.r = r
        self.v = 0
        self.angle = angle
    
    def update(self,ws,hs):
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
    
    def render(self, surface):
        color = lblue
        pg.draw.circle(surface,color,(self.x,self.y),self.r,width=2)
        x2 = self.x+math.cos(self.angle)*(self.r+5)
        y2 = self.y+math.sin(self.angle)*(self.r+5)
        pg.draw.line(surface,color,(self.x,self.y),(x2,y2),width=1)
        
    def shoot(self):
        """
        create a projectile coming from me.
        return the created projectile
        """
        p = Projectile(self.x+math.cos(self.angle)*(self.r+5),self.y+math.sin(self.angle)*(self.r+5),self.v*1.1+1,self.angle)
        return p

# class Player - end

class Projectile:
    def __init__(self,x=100,y=100,v=0,angle=0):
        self.x = x
        self.y = y
        self.v = v
        self.angle = angle
    
    def update(self,ws,hs):
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
    
    def render(self, surface):
        color = red
        pg.draw.circle(surface,color,(self.x,self.y),2,width=2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((720, 480))
        self.ws = self.screen.get_width()
        self.hs = self.screen.get_height()
        
        self.clock = pygame.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.players = []
        self.players.append(Player())
        self.players.append(Player(x=self.ws-100,angle=math.pi))
        
        self.projectiles = []

        
        self.keypressed={} # will store current keyboard pressed
        
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
                
                if event.key == pygame.K_RETURN:
                    self.addProjectile(0)
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                if key == pygame.K_a or key == pygame.K_UP:
                    self.players[0].v += 0.05
                elif key == pygame.K_q or key == pygame.K_DOWN:
                    self.players[0].v = 0
                elif key == pygame.K_q or key == pygame.K_LEFT:
                    self.players[0].angle -= 0.05
                elif key == pygame.K_q or key == pygame.K_RIGHT:
                    self.players[0].angle += 0.05
                elif key == pygame.K_ESCAPE:
                    return True
                    
        return False
        
    def addProjectile(self, numPlayer):
        newProj = self.players[numPlayer].shoot()
        self.projectiles.append(newProj)
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        for p in self.players:
            p.update(self.ws,self.hs)

        for p in self.projectiles:
            p.update(self.ws,self.hs)        
                
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)

        for p in self.players:
            p.render(self.screen)
            
        for p in self.projectiles:
            p.render(self.screen)
            
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


runGame()