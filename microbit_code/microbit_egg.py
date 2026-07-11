# Imports go at the top
from microbit import *
import random

def run_game():
    
    raq_x = 3
    egg_x = random.randint(0,4)
    egg_y = 0
    timeEggDown = running_time() - 10
    pts = 0
    while 1:
    
        if running_time() > timeEggDown:
            duree = 1000 - pts*100
            if duree < 100:
                duree = 100
            timeEggDown = running_time() + duree
            egg_y += 1
            if egg_y == 4:
                if egg_x == raq_x:
                    # win
                    pts += 1
                else:
                    #lost
                    display.show(pts)
                    sleep(2000)
                    pts = 0 # on recommence
                egg_x = random.randint(0,4)
                egg_y = 0
    
        if button_a.was_pressed():
            raq_x -= 1
            if raq_x < 0:
                raq_x = 0
        if button_b.was_pressed():
            raq_x += 1
            if raq_x > 4:
                raq_x = 4
    
        display.clear()
        display.set_pixel(egg_x,egg_y,7)
        display.set_pixel(raq_x,4,9)
    
        sleep( 100 )
    
    


run_game()

