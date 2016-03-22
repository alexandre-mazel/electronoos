# -*- coding: utf-8 -*-

#
# Generate roadmap
# (c) 2016 A.Mazel
#


import cv2
import datetime

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

def drawBigArrow( img, topLeft, bottomRight, lineColor, nThickness = 2, nArrowOffset=40, fillColor = None, nArrowFlag = 3 ):
    """
    
    - nArrowOffset: an offset representing the size of the pointe (if > 0 the point goes to the right)
    - fillColor: the fill color. if set to None: no fill, if set to 0: same as border
    - nArrowFlag: 0: no arrow flag, 1: just right arrow (p6), 2: just left arrow, 3: both arrow
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
    
    print( "DBG: drawBigArrow: topLeft: %s, bottomRight: %s" % (str(topLeft),str(bottomRight)) ) # 6 et 5 inversé dans un cas !?!
    
    p1 = topLeft;
    p2 = (bottomRight[0], topLeft[1]);
    p3 = bottomRight;
    p4 = (topLeft[0], bottomRight[1]);
    
    ycenter = ( p1[1]+p4[1] ) / 2

    print nArrowFlag
    print nArrowFlag & 2
    print nArrowFlag & 1
    if( ( nArrowFlag & 2 ) != 0 ):
        p5 = (p1[0]+nArrowOffset, ycenter)
    else:
        p5 = (p1[0], ycenter )
        
    if( ( nArrowFlag & 1 ) != 0 ):
        p6 = (p2[0]+nArrowOffset, ycenter )
    else:
        p6 = (p2[0], ycenter )

    lineType = 2
    
    listPoint = [p1, p2, p6, p3, p4, p5]
    
    if( fillColor != None ):
        # use an intermediate copy to fill it (bouh) (TODO: optim?)
        imgt = img.copy()
        imgt[::] = (0,0,0)
    else:
        imgt = img # shallow copy
    
    for i in range(len(listPoint) ):
        cv2.line( imgt, listPoint[i], listPoint[(i+1)%len(listPoint)], lineColor, nThickness, lineType );
    
    if( fillColor != None ):
        if( fillColor == 0 ):
            fillColor = lineColor
        mask = numpy.zeros( (imgt.shape[0]+2,imgt.shape[1]+2,1), numpy.uint8)
        center = ( (topLeft[0]+bottomRight[0])/2, (topLeft[1]+bottomRight[1])/2 )
        print( "topLeft: %s, bottomRight: %s, center: %s" % (str(topLeft),str(bottomRight),str(center)) )
        cv2.floodFill( imgt, None, center, lineColor )
        
        # add imgt to img
        
        # create invert mask
        mask_gray = cv2.cvtColor(imgt,cv2.COLOR_BGR2GRAY)
        ret, mask_gray = cv2.threshold(mask_gray, 10, 255, cv2.THRESH_BINARY_INV)
        
        img[:] = cv2.bitwise_or(img,imgt,mask = mask_gray) # remove part under the new shape
        img[:] = cv2.add( img, imgt ) # add two
        
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
    
    
def getDateFromString( strDate ):
    if( len(strDate) == 7 ):
        fmt = "%m/%Y"
        date = datetime.datetime.strptime( strDate, fmt )
    else:
        fmt = "%d/%m/%Y"
        date = datetime.datetime.strptime( strDate, fmt )        
    return date
    
def getDurationInMonth( strStart, strEnd ):
    """
    return a floating time of month between two date.
    eg:
        "03/2016", "06/2016" => 3.
        "01/03/2016", "15/06/2016" => 3.5 # approximation could occurs
    """
    timeStart = getDateFromString( strStart )
    timeEnd = getDateFromString( strEnd )        
    timeDelta = timeEnd - timeStart
    print( "timeDelta.days: %s" % timeDelta.days )
    rDuration = timeDelta.days/30
    print( "INF: duration between %s and %s => %f" % (strStart, strEnd, rDuration) )
    return rDuration

def renderRoadMap( strStartDate, nNbrMonth, aListTaskGroups ):
    """
    aListTaskGroups: a list of group of task line to render: a task line is a bunch of task at the same line. a group of task line are a group of task line with same colors
        eg:
            [    [  [t1, t2], [t3, t4, t5]  ] ,  [  [t6], [t7,t8, t9, t10]  ]     ]
                  -- a group of task list --                 --- a tasklist ---
            
            a task is a list: start date, duration in month, name
    """
    
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
    nMonthW = ( nRealSizeX / nNbrMonth ) - nMonthSpacing
    nMonthH = nRealSizeY
    #~ nMonthH = 50
    for nNumMonth in range(nNbrMonth):
        x = nMargin+nNumMonth*(nMonthW+nMonthSpacing)
        y = nMargin
        drawRoundedRectangle( img, (x, y), (x+nMonthW, y+nMonthH), monthColor, 2, nCornerRadius, 0 )
        strText = getMonthNameAbbrev( nNumMonth ) + " 2016"
        rScale, bl = getTextScaleToFit( strText, (nMonthW-nMonthTextMargin*2, 40), nMonthFont, nMonthFontThickness )
        cv2.putText( img, strText, (x+bl[0]+nMonthTextMargin,y+bl[1]+nMonthTextMargin), nMonthFont, rScale, monthColorText, nMonthFontThickness )

    #~ nNbrTaskLine = len(aListTask)
    nTaskWidth = 30
    aTaskLineColor = [ (199, 133,62), (1, 255, 0), (50, 195,241), (120,76,125) ]
    taskColorText = (0, 0, 0)
    nTaskLineW = 60
    nTaskLineSpacing = 20
    nTaskFont = cv2.FONT_HERSHEY_SIMPLEX
    nTaskFontThickness = 2    
    nTaskTextMargin = 14
    nTaskSizeArrow = 40
    y = 60 + nMargin + nMonthTextMargin
    for nNumTaskLineGroup in range(len(aListTaskGroups)):
        for nNumTaskLine in range(len(aListTaskGroups[nNumTaskLineGroup])):
            y  += (nTaskLineW+nTaskLineSpacing)
            for nNumTask in range(len(aListTaskGroups[nNumTaskLineGroup][nNumTaskLine])):
                nArrowFlag = 3
                strStartTask, rDuration, strText = aListTaskGroups[nNumTaskLineGroup][nNumTaskLine][nNumTask]
                wTask = int(rDuration*nMonthW) + (int(rDuration+0.5)-1)*nMonthSpacing
                decayTime = getDurationInMonth(strStartDate, strStartTask)
                x = nMargin + int(decayTime * nMonthW)
                if( decayTime >= 1. ):
                    x += (int(decayTime+0.5)+0)*nMonthSpacing
                
                xRight = x+wTask-nTaskSizeArrow
                if( xRight > nSizeX - nMargin*2 - nTaskSizeArrow ):
                    xRight = nSizeX - nMargin*2
                    nArrowFlag = 2
                if( x < nMargin ):
                    x = nMargin
                    nArrowFlag &= 1 # remove the 2 bit if set
                print( "x: %s, xr: %s" % (x, xRight) )
                drawBigArrow( img, (x,y), (xRight, y+nTaskLineW), aTaskLineColor[nNumTaskLineGroup], 2, nTaskSizeArrow, 0, nArrowFlag = nArrowFlag )
                
                rScale, bl = getTextScaleToFit( strText, (wTask-nTaskTextMargin*2, nTaskLineW-nTaskTextMargin*2), nTaskFont, nTaskFontThickness )
                print( "rScale: %s" % rScale )
                cv2.putText( img, strText, (x+bl[0]+nTaskTextMargin,y+bl[1]+nTaskTextMargin), nTaskFont, rScale, taskColorText, nTaskFontThickness )
            
    return img
    
# renderRoadMap - end    

startDate = "03/2016"
tl1 = [
                [ startDate, 6., "Ensemble Learning for Face Detection (2D)"],
                #~ [ "06/2016", 3., "Assemblage du banc"],
        ]
        
tl2 = [
                [ "04/2016", 3., "Top Body Skeleton Tracker (3D)"],
        ]        

tl3 = [
                [ "04/2016", 6., "User Recognition (Audio)"],
        ]                

tl4 = [
                [ "02/2016", 9., "Simple Activity Recognition (with static Pepper)"],
        ]              
        
tl20 = [
                [ "02/2016", 2., "Depth Camera Selection"],
        ]              
tl21 = [
                [ "05/2016", 2., "Object Recognition (2D)"],
        ]
        
taskGroup1 = [tl1, tl2,tl3,tl4]
taskGroup2 = [tl20,tl21]
taskGroupList = [taskGroup1, taskGroup2]

img = renderRoadMap( "03/2016", 6, taskGroupList )

strWindowName = "roadmap"
cv2.namedWindow( strWindowName, 0 )
cv2.moveWindow( strWindowName, 0,0 )
cv2.resizeWindow( strWindowName, img.shape[1]/2,img.shape[0]/2 )
cv2.imshow( strWindowName, img )
cv2.waitKey(2500)
