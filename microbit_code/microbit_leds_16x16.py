from microbit import *
import neopixel

nbr_leds = 16*16;
leds = neopixel.NeoPixel(pin1, nbr_leds)

def setpix( x, y, color ):
    if y % 2 == 0:
        leds[x+y*16] = color
    else:
        leds[(15-x)+y*16] = color

leds.fill((0,0,3)) # Toutes en bleue
leds[0] = (63, 63, 0) # la premiere en fuchia
leds.show()

sleep(1000)

setpix(6,0,(255,0,255))
setpix(6,1,(255,0,255))
leds.show()

display.show(Image.FABULOUS)
