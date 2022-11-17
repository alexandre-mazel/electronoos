import copy
import pygame

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
grey = (127, 127, 127)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((720, 480))
        self.clock = pygame.time.Clock()
        self.fps = 60  # Frames per second.
        
        # a game pixel
        self.pixel_img = pygame.Surface((16, 16))
        self.pixel_img.fill(grey)
        
        # a game pixel lighen
        self.pixel_img_lighten = pygame.Surface((16, 16))
        self.pixel_img_lighten.fill(white)
        
        self.w = 40
        self.h = 26
        self.renderworld_x = 20 # left top corner when we start to draw our world
        self.renderworld_y = 20
        
        self.world = [] # a world of w x h size (not optimal: stored as a standard python list and not numpy array)
        # 0: empty
        # 1: filled
        
        for j in range(self.h):
            self.world.append([])
            for i in range(self.w):
                self.world[j].append(0)
        
        self.world[self.h//2][self.w//2] = 1 # allume un point central

        for j in range(8):
            for i in range(8):
                self.world[j+4][i+4] = 1
        
        self.keypressed={}
        self.mousepressed = False
        
        
        
        self.numframe = 0
        self.bPause = 0
        
    def updateLife( self ):
        old = copy.deepcopy(self.world) # create a duplication of the world
        
        for j in range(1,self.h-1):
            for i in range(1,self.w-1):
                count_neighbours =      old[j-1][i-1] \
                                                + old[j-1][i+0] \
                                                + old[j-1][i+1] \
                                                + old[j+0][i-1] \
                                                \
                                                + old[j+0][i+1] \
                                                + old[j+1][i-1] \
                                                + old[j+1][i+0] \
                                                + old[j+1][i+1]
                if count_neighbours == 3:
                    self.world[j][i] = 1
                else:
                    self.world[j][i] = 0
    
    def update( self ):
        """
        return True if user want to quit
        """
        
        self.numframe += 1
        
        if self.numframe % 50 == 0 and not self.bPause:
            self.updateLife()
        
        self.clock.tick(self.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
                
            if event.type == pygame.KEYDOWN:
                
                """
                #work well but only when changing state from nothing to keydown
                if event.key == pygame.K_a:
                    self.square_pos[1] += 1
                elif event.key == pygame.K_q:
                    self.square_pos[1] -= 1
                """
                    
                self.keypressed[event.key] = 1
                
            if event.type == pygame.KEYUP:
                self.keypressed[event.key] = 0
                
                # ici les touches a  usage unique
                if event.key == pygame.K_p:
                    self.bPause = not self.bPause
                    print("bPause: %s" % self.bPause )
            
            for key, bPressed in self.keypressed.items():
                if bPressed:
                    if key == pygame.K_ESCAPE:
                        return True
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousepressed = True
                
            if event.type == pygame.MOUSEBUTTONUP:
                self.mousepressed = False
                
            if self.mousepressed:
                pos = pygame.mouse.get_pos()
                #~ print(pos)
                wpix, hpix = self.pixel_img.get_size()
                xgame = (pos[0] - self.renderworld_x)//(wpix+1)
                ygame = (pos[1] - self.renderworld_y)//(hpix+1)
                if xgame >= 0 and xgame < self.w and ygame >= 0 and ygame < self.h:
                    self.world[ygame][xgame] = 1
                    
                    
        return False

    def render(self):
        self.screen.fill(black)
        wpix, hpix = self.pixel_img.get_size()
        for j in range(self.h):
            for i in range(self.w):
                x = self.renderworld_x+i*(wpix+1)
                y = self.renderworld_y+j*(hpix+1)
                if self.world[j][i] == 1:
                    self.screen.blit(self.pixel_img_lighten, [x,y,x+wpix,y+hpix] )
                else:
                    self.screen.blit(self.pixel_img, [x,y,x+wpix,y+hpix] )
        
        pygame.display.update()  # Or pygame.display.flip()
        
# class Game - end

def startGame():
    game = Game()
    while 1:
        bQuit = game.update()
        if bQuit:
            break
        game.render()
        
# startGame - end

startGame()