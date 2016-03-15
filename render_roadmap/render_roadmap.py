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

def drawRoundedRectangle( img, topLeft, bottomRight, lineColor, nThickness, nCornerRadius, fillColor = None ):
    """
    - cornerRadius A positive int value defining the radius of the round corners.
    - fillColor: the fill color. if set to None: no fill, if set to 0: same as border
    """
    
    """
    corners:
       p1 - p2
       |       |
       p4 - p3
    """
    p1 = topLeft;
    p2 = (bottomRight[0], topLeft[1]);
    p3 = bottomRight;
    p4 = (topLeft[0], bottomRight[1]);

    lineType = 2
    # draw straight lines
    cv2.line( img, (p1[0]+nCornerRadius,p1[1]), (p2[0]-nCornerRadius,p2[1]), lineColor, nThickness, lineType );
    cv2.line( img, (p2[0],p2[1]+nCornerRadius), (p3[0],p3[1]-nCornerRadius), lineColor, nThickness, lineType );
    cv2.line( img, (p4[0]+nCornerRadius,p4[1]), (p3[0]-nCornerRadius,p3[1]), lineColor, nThickness, lineType );
    cv2.line( img, (p1[0],p1[1]+nCornerRadius), (p4[0],p4[1]-nCornerRadius), lineColor, nThickness, lineType );

    # draw arcs
    cv2.ellipse( img, (p1[0]+nCornerRadius, p1[1]+nCornerRadius), ( nCornerRadius, nCornerRadius ), 180, 0., 90., lineColor, nThickness, lineType );
    cv2.ellipse( img, (p2[0]-nCornerRadius, p2[1]+nCornerRadius), ( nCornerRadius, nCornerRadius ), 270, 0., 90., lineColor, nThickness, lineType );
    cv2.ellipse( img, (p3[0]-nCornerRadius, p3[1]-nCornerRadius), ( nCornerRadius, nCornerRadius ), 0, 0., 90., lineColor, nThickness, lineType );
    cv2.ellipse( img, (p4[0]+nCornerRadius, p4[1]-nCornerRadius), ( nCornerRadius, nCornerRadius ), 90, 0., 90., lineColor, nThickness, lineType );
    #~ cv2.ellipse( img, p2+(-nCornerRadius, nCornerRadius), ( nCornerRadius, nCornerRadius ), 270.0, 0, 90, lineColor, nThickness, lineType );
    #~ cv2.ellipse( img, p3+(-nCornerRadius, -nCornerRadius), ( nCornerRadius, nCornerRadius ), 0.0, 0, 90, lineColor, nThickness, lineType );
    #~ cv2.ellipse( img, p4+(nCornerRadius, -nCornerRadius), ( nCornerRadius, nCornerRadius ), 90.0, 0, 90, lineColor, nThickness, lineType );
    
    if( fillColor != None ):
        if( fillColor == 0 ):
            fillColor = lineColor
        #~ mask = numpy.zeros( (img.shape[0]+2,img.shape[1]+2,1), numpy.uint8)
        center = ( (topLeft[0]+bottomRight[0])/2, (topLeft[1]+bottomRight[1])/2 )
        cv2.floodFill( img, None, center, lineColor )
# drawRoundedRectangle - end

def renderRoadMap( strStartDate, nNbrMonth, aListTask ):
    nSizeX = 800
    nSizeY = 600
    nMargin = 100
    nRealSizeX = nSizeX - nMargin/2
    nRealSizeY = nSizeY - nMargin/2
    img = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    img[::] = (255,255,255)

    nCornerRadius = 20
    
    monthColor = (243, 226, 207)
    nMonthSpacing = 10
    nW = ( nRealSizeX / nNbrMonth ) - nMonthSpacing
    nH = nRealSizeY
    for nNumMonth in range(nNbrMonth):
        x = nMargin+nNumMonth*(nW+nMonthSpacing)
        y = nMargin
        drawRoundedRectangle( img, (x, y), (x+nW, y+nH), monthColor, 2, nCornerRadius, 0 )

    return img
    
# renderRoadMap - end    


taskList = []
img = renderRoadMap( "03/2016", 6, taskList )

strWindowName = "roadmap"
cv2.namedWindow( strWindowName )
cv2.imshow( strWindowName, img )
cv2.moveWindow( strWindowName, 0,0 )
cv2.waitKey(1500)
