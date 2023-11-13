from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

def runLoopOscHandler(game, ip = "127.0.0.1", port = 8002):
    
    def filter_handler(address, *args):
        print(f"{address}: {args}")


    dispatcher = Dispatcher()
    dispatcher.map("/global", filter_handler)
    dispatcher.map("/u1", filter_handler)
    dispatcher.map("/u2", filter_handler)

    async def loop(game):
        """Example main loop that only runs for 10 iterations before finishing"""
        while 1:
            #~ print(f"Loop...")
            await asyncio.sleep(0.04) # 25fps
            bQuit = game.handleInput()
            game.update()
            if bQuit:
                break
            game.render()


    async def init_main(game):
        print("Running OSC Server on %s:%s" % (ip,port))
        server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

        await loop(game)  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


    asyncio.run(init_main(game))
    
# runLoopOscHandler - end
    
    
import pygame as pg

successes, failures = pg.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)

fontTitleViewer = pg.font.SysFont('Arial', 16)

class Viewer:
    """
    An oscilloscope like to view a value over time
    """
    def __init__(self,x=10,y=10,w=200,h=100,title="Viewer"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.color = (255,244,255)
        self.text_surface = fontTitleViewer.render(self.title, True, self.color)
    
    def update(self,rVal):
        self.value.append(rVal)
        
    def render(self, surf):
        color = self.color
        x,y = self.x,self.y
        x2 = self.x+self.w
        y2 = self.y+self.h
        w = 1
        htitle=24
        titlemargin = 4
        pg.draw.line(surf,color,(x,y),(x2,y),width=w)
        pg.draw.line(surf,color,(x,y+htitle),(x2,y+htitle),width=w)
        pg.draw.line(surf,color,(x,y),(x,y2),width=w)
        pg.draw.line(surf,color,(x,y2),(x2,y2),width=w)
        pg.draw.line(surf,color,(x2,y),(x2,y2),width=w) 
        surf.blit(self.text_surface, (x+titlemargin,y+titlemargin))    
        
        surf.set_at((x+10, y+htitle+4), (255,255,233)) 
        
    

class Object:
    def __init__(self,x=10,y=10,w=32,h=32):
        self.x = w
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0

# class Object - end

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((720, 480))
        self.clock = pg.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.square = Object()
        self.square.img = pg.Surface((self.square.w, self.square.h))
        self.square.img.fill(white)
        self.square.x = 0
        self.square.y = 0
        self.square.vx = 5
        self.square.vy = 0
        
        self.keypressed={} # will store current keyboard pressed
        
        self.viewers = []
        self.viewers.append(Viewer())
        
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
                
            if event.type == pg.KEYDOWN:     
                print("DBG: key '%s' pressed" % event.key )
                self.keypressed[event.key] = 1
                
            if event.type == pg.KEYUP:
                self.keypressed[event.key] = 0
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                if key == pg.K_a or key == pg.K_UP:
                    #~ self.square.y -= 1
                    self.square.vy -= 1
                elif key == pg.K_q or key == pg.K_DOWN:
                    self.square.y += 1
                elif key == pg.K_ESCAPE:
                    return True
                    
        return False
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        self.square.x += self.square.vx
        self.square.y += self.square.vy
        
        self.square.vy += 0.2
        
        # out of screen test
        if      (self.square.vx > 0 and self.square.x + self.square.w > self.screen.get_width()) \
            or (self.square.vx < 0 and self.square.x < 0) \
            :
            self.square.vx *= -1
            
        if self.square.y < 0: 
            self.square.y = 0
        if self.square.vy > 0 and self.square.y + self.square.h> self.screen.get_height(): 
            self.square.y = self.screen.get_height()-self.square.h
            self.square.vx *=0.9
            self.square.vy *= -0.7
            if abs(self.square.vy)<1.:
                self.square.vy = 0
            if abs(self.square.vx)<0.2:
                self.square.vx = 0
                
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)
        self.screen.blit(self.square.img, [self.square.x,self.square.y,self.square.x+self.square.w,
                                                                                                self.square.y+self.square.h] )
                                                                                                
        self.screen.set_at((100, 300), (255,255,233)) 
        self.screen.set_at((110, 300), (255,255,233)) 
        
        for v in self.viewers:
            v.render(self.screen)
        
        pg.display.update()  # or pg.display.flip()
        
# class Game - end

game = Game()


runLoopOscHandler(game)
