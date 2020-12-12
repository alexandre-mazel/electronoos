import pygame
import cv2
import os
import time
import opensimplex
import sys

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

def bgr2rgb(col):
    b = col[0]
    col[0] = col[2]
    col[2] = b
    return col

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
    
def warp(x,screensize):
    if x < 0:
        x += screensize
    if x >= screensize:
        x -= screensize
    return x
    

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
    

bUseModel = 1 # force the trace to draw something
if bUseModel:
    #~ model = cv2.imread(misctools.getPathData() + "landscape-bw.jpg", cv2.IMREAD_GRAYSCALE)
    model = cv2.imread(misctools.getPathData() + "logo_nike.jpg", cv2.IMREAD_GRAYSCALE)
    model = cv2.imread(misctools.getPathData() + "face_bw1.jpg", cv2.IMREAD_GRAYSCALE)
    if model.shape[1] > 1300:
        model = cv2.resize(model,None,fx=0.5,fy=0.5)
    screenh,screenw = model.shape[:2]
    
bUseModelRGB = 0    
if bUseModelRGB:
    #~ model = cv2.imread(misctools.getPathData() + "landscape-bw.jpg", cv2.IMREAD_GRAYSCALE)
    model = cv2.imread(misctools.getPathData() + "landscape.jpg")
    screenh,screenw = model.shape[:2]



size = (screenw, screenh)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My First Game")

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()
 
bContinue = True

nCptImageFps = 0
nCptImageTotal = 0
timeBegin = time.time()


t = 0
dt = 1/60.
x = screenw // 2
y = screenh // 2

x2 = screenw // 2 + 100
y2 = screenh // 2

x3 = screenw // 2 - 100
y3 = screenh // 2

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
    dx = osx.noise2d(t,0)*0.2
    dy = osx.noise2d(t,1)*0.2
    #~ print("t: %5.2f, dx: %f, dy: %f" % (t,dx, dy) )
    
    if bUseModel:
        grey = model[int(clamp(y,0,screenh-1)),int(clamp(x,0,screenw-1))]
        
        dx *= 20
        dy *= 20
        # slowdown if dark
        dx /= (256-grey)*0.1
        dy /= (256-grey)*0.1
        
        
    x += dx
    y += dy
    
    if bUseModelRGB:
        dx2 = osx.noise2d(t,10)*0.2
        dy2 = osx.noise2d(t,20)*0.2        
        dx3 = osx.noise2d(t,30)*0.2
        dy3 = osx.noise2d(t,40)*0.2
        
        x2 += dx2
        y2 += dy2
        x3 += dx3
        y3 += dy3
        
    if bUseModel or bUseModelRGB:
        # warp
        if x < 0:
            x += screenw
        if x >= screenw:
            x -= screenw
        if y < 0:
            y += screenh
        if y >= screenh:
            y -= screenh
            
        if bUseModelRGB:
            x2 = warp(x2,screenw)
            y2 = warp(y2,screenh)
            x3 = warp(x3,screenw)
            y3 = warp(y3,screenh)
            
            
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
    inc = -1
    new_color = (new_color[0]+inc,new_color[1]+inc,new_color[2]+inc)
    new_color = clamp_list(new_color,0,255)
    #~ print(new_color)
    
    if bUseModelRGB:
        new_color = model[yr,xr]
        new_color = bgr2rgb(new_color)
        if 1:
            # 3 pixels per composantes
            xr2 = int(x2)
            yr2 = int(y2)
            xr3 = int(x3)
            yr3 = int(y3)

            col = screen.get_at((xr,yr))
            col_model = model[yr,xr]
            #~ print(col)
            col = (col_model[2],col[1],col[2])
            screen.set_at( (xr,yr), col )
            
            col = screen.get_at((xr2,yr2))
            col_model = model[yr2,xr2]
            #~ print(col)
            col = (col[0],col_model[1],col[2])
            screen.set_at( (xr2,yr2), col )

            col = screen.get_at((xr3,yr3))
            col_model = model[yr3,xr3]
            #~ print(col)
            col = (col[0],col[1],col_model[0])
            screen.set_at( (xr3,yr3), col )
            
            
    else:
        if bUseModel:
            screen.set_at( (xr,yr), new_color )
        else:
            pygame.draw.circle(screen, new_color, [xr,yr], 1)

 

    # --- Go ahead and update the screen with what we've drawn.
    if (nCptImageTotal % 200) == 0:
        pygame.display.flip()
        
    if 1:
        if (nCptImageTotal % (500*1000)) == 0:
            name = "/images_generated/" + misctools.getFilenameFromTime() + ".png"
            print("t:%7.2fs, saving image..." % t)
            pygame.image.save(screen, name)
                
        if 0:
            if (nCptImageTotal % (50*1000)) == 0:
                #estompe tout l'ecran
                for j in range(screenh):
                    for i in range(screenw):
                        col = screen.get_at([i,j])
                        for k in range(3):
                            if col[k] < 255:
                                col[k] = col[k]+1
                        screen.set_at([i,j],col)
        

    # --- Limit to 60 frames per second
    clock.tick(6000)
    t += dt
    
    nCptImageTotal += 1
    
    # fps counting
    nCptImageFps += 1
    if nCptImageFps > 10000 or time.time() - timeBegin > 5:
        duration = time.time() - timeBegin
        print("INF: %5.1ffps" % ( nCptImageFps / duration) )
        nCptImageFps = 0
        timeBegin = time.time()

#Once we have exited the main program loop we can stop the game engine:
pygame.quit()