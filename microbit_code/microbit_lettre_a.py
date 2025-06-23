from microbit import *
for i in range(4):
    display.set_pixel(0,1+i,9)
    display.set_pixel(4,1+i,9)

for i in range(3):
    display.set_pixel(1+i,0,9)
    display.set_pixel(1+i,3,9)