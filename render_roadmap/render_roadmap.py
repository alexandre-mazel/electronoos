# -*- coding: utf-8 -*-

#
# Generate roadmap
# (c) 2016 A.Mazel
#

import cv2

import math
import mutex
import numpy
import sys
import time

sys.path.insert( 0, "../../protolab" )
import protolab.geometry as geo

def renderRoadMap( strStartDate, nNbrMonth, aListTask ):
    nSizeX = 800
    nSizeY = 600
    img = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    img[::] = (255,255,255)
    for nNumMonth in range(nNbrMonth):
        pass
    windowName = "roadmap"
    cv2.namedWindow( windowName )
    cv2.imshow( windowName, img )
    cv2.waitKey(1500)
    
# renderRoadMap - end    


taskList = []
renderRoadMap( "03/2016", 6, taskList )