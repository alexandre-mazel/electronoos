from microbit import *


steps=0
display.show(steps, wait=False)

while True:
    if accelerometer.was_gesture('shake'):
        steps += 1
        if steps < 10:
            display.show(steps, wait=False)
        else:
            display.scroll(steps, delay=100, wait=False)