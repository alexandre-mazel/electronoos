import pygame

successes, failures = pygame.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
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
        self.pixel_img.fill(white)
        
        self.w = 40
        self.h = 20
        self.world = [] # a world of w x h size (not optimal: stored as a standard python list and not numpy array)
        # 0: empty
        # 1: filled
        
        for j in range(self.h):
            self.world.append([])
            for i in range(self.w):
                self.world[j].append(0)
        
        self.keypressed={}
    
    def update(self):
        """
        return True if user want to quit
        """
        
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
                
            for key, bPressed in self.keypressed.items():
                if bPressed:
                    if key == pygame.K_ESCAPE:
                        return True
                    
                    
        return False

    def render(self):
        self.screen.fill(black)
        wpix, hpix = self.pixel_img.get_size()
        for j in range(self.h):
            for i in range(self.w):
                x = 20+i*(wpix+1)
                y = 20+j*(hpix+1)
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