#include all necessary packages to get LEDs to work with Raspberry Pi
import time
import board
import neopixel

#Initialise two strips variables, provide the GPIO Data Pin
#utilised and the amount of LED Nodes and brightness (0 to 1 value)
pixels1 = neopixel.NeoPixel(board.D18, 30, brightness=1)
pixels2 = neopixel.NeoPixel(board.D21, 6, brightness=1)

#Focusing on a particular strip, use the command Fill to make it all a single colour
#based on decimal code R, G, B. Number can be anything from 255 - 0. Use a RGB Colour
#Code Chart Website to quickly identify a desired fill colour.
pixels1.fill((0, 255, 0))
pixels2.fill((0, 0, 255))

#Sleep for one second, and then code repeats for different colour combinations. Light changes
#Could happen instead in response to certain buttons being pressed or due to threshold values
time.sleep(1.5)

pixels1.fill((200, 200, 0))
pixels2.fill((0, 200, 200))

time.sleep(1.5)

pixels1.fill((50, 70, 215))
pixels2.fill((215, 50, 70))

time.sleep(1.5)

pixels1.fill((0, 0, 0))
pixels2.fill((0, 0, 0))