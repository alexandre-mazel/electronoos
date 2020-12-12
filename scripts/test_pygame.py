import pygame
import os
import time
import opensimplex

def clamp( x, lowerlimit = 0, upperlimit = 1 ):
    if x < lowerlimit: return lowerlimit
    if x > upperlimit: return upperlimit
    return x
    
def clamp_list(a,lowerlimit = 0, upperlimit = 1 ):
    ret = list(a)
    for i in range(len(ret)):
        ret[i] = clamp(ret[i],lowerlimit = lowerlimit, upperlimit=upperlimit)
    if isinstance(a, tuple):
        ret = tuple(ret)
    return ret
    

pygame.init()

# Define some colors
BLACK = ( 0, 0, 0,100)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)

#set windows position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (4,40)

screenw = 1200
screenh = 800

if 1:
    # full screen on my ms tab4
    screenw = 2736//2
    screenh = 1824//2
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)


size = (screenw, screenh)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My First Game")

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
 
bContinue = True

nCptImage = 0
timeBegin = time.time()

t = 0
dt = 1/60.
x = screenw // 2
y = screenh // 2

osx = opensimplex.OpenSimplex()
screen.fill(WHITE)

while bContinue:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
              bContinue = False
              
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                bContinue = False
            
            
    #logic
    dx = osx.noise2d(t,0)*1
    dy = osx.noise2d(t,1)*1
    #~ print("t: %5.2f, dx: %f, dy: %f" % (t,dx, dy) )
    x += dx
    y += dy

    #rendering
    #~ screen.fill(WHITE)
    
    #~ pygame.draw.rect(screen, RED, [55, 200, 100, 70],0)
    #~ pygame.draw.line(screen, GREEN, [0, 0], [100, 100], 5)
    #~ pygame.draw.ellipse(screen, BLACK, [20,20,250,100], 2)
    
    xr = int(x)
    yr = int(y)
    while xr < 0 or xr >= screenw:
        #~ print("begin: %s" % xr)
        if xr < 0:
            xr = abs(xr)
        if xr >= screenw:
            xr = 2*(screenw-1) - xr
        #~ print(xr)
        
    while yr < 0 or yr >= screenh:
        if yr < 0:
            yr = abs(yr)
        if yr >= screenh:
            yr = 2*(screenh-1) - yr
        
    new_color = screen.get_at((xr-0,yr-0))
    inc = -10
    new_color = (new_color[0]+inc,new_color[1]+inc,new_color[2]+inc)
    new_color = clamp_list(new_color,0,255)
    #~ print(new_color)
    
    pygame.draw.circle(screen, new_color, [xr,yr], 1)

 

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(6000)
    t += dt
    
    # fps counting
    nCptImage += 1
    if nCptImage > 10000 or time.time() - timeBegin > 5:
        duration = time.time() - timeBegin
        print("INF: %5.1ffps" % ( nCptImage / duration) )
        nCptImage = 0
        timeBegin = time.time()

#Once we have exited the main program loop we can stop the game engine:
pygame.quit()