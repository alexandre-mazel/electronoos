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
    
    if( fillColor != None ):
        if( fillColor == 0 ):
            fillColor = lineColor
        #~ mask = numpy.zeros( (img.shape[0]+2,img.shape[1]+2,1), numpy.uint8)
        center = ( (topLeft[0]+bottomRight[0])/2, (topLeft[1]+bottomRight[1])/2 )
        cv2.floodFill( img, None, center, lineColor )
# drawRoundedRectangle - end

def drawBigArrow( img, topLeft, bottomRight, lineColor, nThickness = 2, nArrowOffset=40, fillColor = None ):
    """
    
    - nArrowOffset: an offset representing the size of the pointe (if > 0 the point goes to the right)
    - fillColor: the fill color. if set to None: no fill, if set to 0: same as border
    """
    
    """
    corners:
       p1 --------------- p2
          \                   \
       p5 \                   \ p6
           /                    /
          /                    /
       p4 ---------------- p3
    """
    p1 = topLeft;
    p2 = (bottomRight[0], topLeft[1]);
    p3 = bottomRight;
    p4 = (topLeft[0], bottomRight[1]);
    p5 = (p1[0]+nArrowOffset,( p1[1]+p4[1] ) / 2 )
    p6 = (p2[0]+nArrowOffset,( p1[1]+p4[1] ) / 2 )

    lineType = 2
    
    listPoint = [p1, p2, p6, p3, p4, p5]
    for i in range(len(listPoint) ):
        cv2.line( img, listPoint[i], listPoint[(i+1)%len(listPoint)], lineColor, nThickness, lineType );
    
    if( fillColor != None ):
        if( fillColor == 0 ):
            fillColor = lineColor
        mask = numpy.zeros( (img.shape[0]+2,img.shape[1]+2,1), numpy.uint8)
        center = ( (topLeft[0]+bottomRight[0])/2, (topLeft[1]+bottomRight[1])/2 )
        cv2.floodFill( img, None, center, lineColor )
# drawBigArrow - end

def getTextScaleToFit( strText, rectToFit, fontFace, nThickness = 1 ):
    """
    Compute the biggest scale to fit in some rectangle
    return [rScale, tl_to_center]
        - rScale: scale to render
        - tl_to_center: the bottom left point to render the font in the rectToFit for the font to be centered
    """
    rScale = 2.
    while( rScale > 0. ):
        rcRendered, baseline = cv2.getTextSize( strText, fontFace, rScale, nThickness )
        if( rcRendered[0] < rectToFit[0] and rcRendered[1] < rectToFit[1] ):
            break
        rScale -= 0.1
    
    return [rScale, ( (rectToFit[0]-rcRendered[0]) / 2,rectToFit[1]-(rectToFit[1]-rcRendered[1]) / 2 )]
    
def getMonthName( nNumMonth ):
    aMonth = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return aMonth[nNumMonth]

def getMonthNameAbbrev( nNumMonth ):
    aMonth = ["Jan", "Feb", "March", "April", "May", "June", "July", "August", "Sept", "Oct", "Nov", "Dec"]
    return aMonth[nNumMonth]

def renderRoadMap( strStartDate, nNbrMonth, aListTask ):
    nSizeX = 1600
    nSizeY = 800
    nMargin = 20
    nRealSizeX = nSizeX - nMargin*2
    nRealSizeY = nSizeY - nMargin*2
    img = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    img[::] = (255,255,255)

    nCornerRadius = 20
    monthColor = (243, 226, 207)
    monthColorText = (212, 161, 99)
    nMonthSpacing = 20
    nMonthFont = cv2.FONT_HERSHEY_SIMPLEX
    nMonthFontThickness = 2
    nMonthTextMargin = 20
    nW = ( nRealSizeX / nNbrMonth ) - nMonthSpacing
    nH = nRealSizeY
    #~ nH = 50
    for nNumMonth in range(nNbrMonth):
        x = nMargin+nNumMonth*(nW+nMonthSpacing)
        y = nMargin
        drawRoundedRectangle( img, (x, y), (x+nW, y+nH), monthColor, 2, nCornerRadius, 0 )
        strText = getMonthNameAbbrev( nNumMonth ) + " 2016"
        rScale, bl = getTextScaleToFit( strText, (nW-nMonthTextMargin*2, 40), nMonthFont, nMonthFontThickness )
        cv2.putText( img, strText, (x+bl[0]+nMonthTextMargin,y+bl[1]+nMonthTextMargin), nMonthFont, rScale, monthColorText, nMonthFontThickness )

    nNbrTaskLine = len(aListTask)
    nTaskWidth = 50
    for nNumTask in range(2):
        drawBigArrow( img, (100,100), (500, 200), (15, 56, 56), 2, 40, 0 )
    return img
    
# renderRoadMap - end    


taskList = []
img = renderRoadMap( "03/2016", 6, taskList )

strWindowName = "roadmap"
cv2.namedWindow( strWindowName, 0 )
cv2.moveWindow( strWindowName, 0,0 )
cv2.resizeWindow( strWindowName, img.shape[1]/2,img.shape[0]/2 )
cv2.imshow( strWindowName, img )
cv2.waitKey(2500)