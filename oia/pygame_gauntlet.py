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

class Object:
    def __init__(self,x=10,y=10,w=32,h=32):
        self.x = w
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0
# class Object - end

class Player:
    def __init__(self,x=100,y=100,r=10,angle=0):
        self.x = x
        self.y = y
        self.r = r
        self.v = 0
        self.angle = angle
    
    def update(self):
        self.x += math.cos(self.angle)*self.v
        self.y += math.sin(self.angle)*self.v
    
    def render(self, surface):
        color = (255,255,0)
        pg.draw.circle(surface,color,(self.x,self.y),self.r,width=2)
        x2 = self.x+math.cos(self.angle)*(self.r+5)
        y2 = self.y+math.sin(self.angle)*(self.r+5)
        pg.draw.line(surface,color,(self.x,self.y),(x2,y2),width=1)

# class Object - end

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
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        for p in self.players:
            p.update()
        
                
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)

        for p in self.players:
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