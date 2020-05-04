# -*- coding: utf-8 -*-

import os
import sys
print sys.version

import ctypes
import random
import struct
import time

import cv2 # manually copied cv2.pyd to lib/site-packages
import numpy # pip install numpy # pip: python get-pip.py

def getMousePosition():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]
        
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def moveMouse( x, y ):    
    setCursorPos = ctypes.windll.user32.SetCursorPos
    sendMouseEvent = ctypes.windll.user32.mouse_event

    setCursorPos(x,y)
    
def moveMouseAndClick( x, y ):    
    setCursorPos = ctypes.windll.user32.SetCursorPos
    sendMouseEvent = ctypes.windll.user32.mouse_event

    setCursorPos(x,y)
    sendMouseEvent( 2,0,0,0,0)
    sendMouseEvent( 4,0,0,0,0)
    
def moveMouseRandomly():
    print( "Move mouse radomly to prevent screensaver (Ctrl+c to quit)")
    while True:
        x,y = getMousePosition()
        if random.random() > 0.9:
            x = 0
            y = 0
            moveMouseAndClick(x,y)
        else:
            x += (int)(random.random()*10-5)
            y += (int)(random.random()*10-5)
            moveMouse(x,y)
        time.sleep(10)
    
moveMouseRandomly()
    