import os
import RPi.GPIO as GPIO
import time

#            o  o
#            o  o
#            o  o  <-- GND
#            o  o
#            o  o
# 17 --> o  o <-- 18
#            o  o
#            o  o
#            o  o
#            o  o
#            o  o
#            o  o
#            o  o

# gpio Gnd to thumb joystick gnd
# and pin 18 to tj SW

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

bLastState = 0

while True:
    input_state = GPIO.input(18)
    bPressed = input_state == False
    if( bLastState != bPressed ):
        bLastState  = bPressed
        if( bPressed ):
            os.system( "mpg123 the_voice_button.mp3&" )
            print('Button Pressed')
        else:
            print('Button Released')
        
    time.sleep(0.01)
        