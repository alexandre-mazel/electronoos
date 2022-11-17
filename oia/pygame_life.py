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
        
        self.square_img = pygame.Surface((32, 32))
        self.square_img.fill(white)
        self.square_pos = [0,0]
        
        self.keypressed={}
    
    def update(self):
        self.clock.tick(self.fps)
        
        self.square_pos[0] += 1

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
                    if key == pygame.K_a:
                        self.square_pos[1] += 1
                    elif key == pygame.K_q:
                        self.square_pos[1] -= 1
                    elif key == pygame.K_ESC:
                        self.square_pos[1] -= 1
                    
        return False

    def render(self):
        self.screen.fill(black)
        self.screen.blit(self.square_img, [self.square_pos[0],self.square_pos[1],self.square_pos[0]+32,self.square_pos[1]+32] )
        
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