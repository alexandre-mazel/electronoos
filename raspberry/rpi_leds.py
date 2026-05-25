#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

 # a lancer en sudo, sinon ca: RuntimeError: ws2811_init failed with code -5 (mmap() failed)
 # ou alors, faire un: sudo usermod -aG audio,video,gpio,plugdev pi
 #  sudo usermod -aG audio,video,gpio,plugdev username
 # ici: sudo usermod -aG gpio na
 
import time
from rpi_ws281x import *
import argparse
import random

# LED strip configuration:
LED_COUNT      = 16     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


LED_COUNT      = 844 # 383 * 3# 383 par barres ? # Fossilation: 842 a droite et 844 a gauche!

nbr_leds = LED_COUNT

#~ ORDER = rpi_ws281x.RGB # default (TODO: test !) (could also be GRB)
STRIP_TYPE = None
STRIP_TYPE = rpi_ws281x.RGBW # When using RGBW (could also be GRBW)

import _rpi_ws281x as ws
#~ print(dir(ws))
STRIP_TYPE = ws.SK6812_STRIP_GRBW


# Define functions which animate LEDs in various ways.
def colorFull(strip, color):
    """Wipe color across display a pixel at a time."""
    print("INF: colorFull: %x" % color )
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=10):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
                
def init_strip( nbr_leds ):
    """
    Init strip with standard settings
    """
    
    print( "INF: init_strip: initing strip with %d led(s)" % nbr_leds )
    
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel( nbr_leds, LED_PIN, LED_FREQ_HZ, LED_DMA, 
        LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, strip_type=STRIP_TYPE, 
        #~ use_gpiochip=True # permits to use it without root privilege
    )
    # Intialize the library (must be called once before other functions).
    strip.begin()
    return strip

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    strip = init_strip( LED_COUNT )

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            

            #~ for i in range(4 ):
            while 1:
                colorFull( strip, 0xFFFFFF )
                time.sleep(1)
                colorFull( strip, 0xFF000000 )
                time.sleep(1)
                colorFull( strip, 0xFFFFFFFF )
                time.sleep(1)
                colorFull( strip, 0x0000FF )
                time.sleep(1)
                colorFull( strip, 0x00FF00 )
                time.sleep(1)
                colorFull( strip, 0xFF0000 )
                time.sleep(1)
                colorFull( strip, 0x0 )
                time.sleep(1)

            print ('Color wipe animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            colorWipe(strip, Color(0, 0, 255))  # Green wipe
            print ('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            print ('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
