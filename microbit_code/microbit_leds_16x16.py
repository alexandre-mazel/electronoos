from microbit import *
import neopixel

nbr_leds = 16*16;
leds = neopixel.NeoPixel(pin1, nbr_leds)

def setpix( x, y, color ):
    coef = 8
    color = (color[0]//coef,color[1]//coef,color[2]//coef)  # dimming
    if y % 2 == 0:
        leds[x+y*16] = color
    else:
        leds[(15-x)+y*16] = color
        
        
        
def draw_tetris():
    lblue = (80,80,255)
    yellow = (255,255,40)
    red = (255,0,0)
    purple = (255,0,255)
    
    setpix(8,15,lblue)
    setpix(8,14,lblue)
    setpix(8,13,lblue)
    setpix(8,12,lblue)
    
    setpix(9,15,yellow)
    setpix(10,15,yellow)
    setpix(9,14,yellow)
    setpix(10,14,yellow)
    
    setpix(11,15,red)
    setpix(11,14,red)
    setpix(12,14,red)
    setpix(12,13,red)
    
    setpix(9,8,purple)
    setpix(10,8,purple)
    setpix(11,8,purple)
    setpix(10,7,purple)
    
leds.fill((0,0,3)) # Toutes en bleue
leds[0] = (63, 63, 0) # la premiere en fuchia
leds.show()

sleep(700)

leds.fill((0,0,0)) # raz
setpix(6,0,(255,0,255))
setpix(6,1,(255,0,255))
leds.show()
sleep(700)

leds.fill((0,0,0)) # raz
draw_tetris()
leds.show()

display.show(Image.FABULOUS)
