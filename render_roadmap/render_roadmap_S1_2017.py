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

def isInImage( pt, img ):
    w  = img.shape[1]
    h  = img.shape[0]
    if( pt[0] < 0 or pt[0] > w ):
        return False
    if( pt[1] < 0 or pt[1] > h ):
        return False
    return True
# isInImage - end    
    
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
        if isInImage( center, imgt ):
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
    return aMonth[nNumMonth%12]
    
    
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
    if( rDuration < -1 ):
        rDuration += 1 # TODO: why is there an error in this case?
    print( "INF: duration between %s and %s => %f" % (strStart, strEnd, rDuration) )
    return rDuration

def renderRoadMap( strStartDate, nNbrMonth, aListTaskGroups, aLegends = [] ):
    """
    aListTaskGroups: a list of group of task line to render: a task line is a bunch of task at the same line. a group of task line are a group of task line with same colors
        eg:
            [    [  [t1, t2], [t3, t4, t5]  ] ,  [  [t6], [t7,t8, t9, t10]  ]     ]
                  -- a group of task list --                 --- a tasklist ---
            
            a task is a list: start date, duration in month, name, [color group] => you can manually give a color index of another group. eg 1 => the color of the 2nd group
            
        - strStartDate: the start date, eg: "09/2016"
        - aLegends: a list of legends (one per group of tasks)
        
    """
    rMagnify = 2
    nSizeX = 1600*rMagnify
    nSizeY = 1040*rMagnify
    nMargin = 20*rMagnify
    nRealSizeX = nSizeX - nMargin*2
    nRealSizeY = nSizeY - nMargin*2
    img = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    img[::] = (255,255,255)

    nCornerRadius = 20*rMagnify
    monthColor = (243, 226, 207)
    monthColorText = (212, 161, 99)
    nMonthSpacing = 20*rMagnify
    nMonthFont = cv2.FONT_HERSHEY_SIMPLEX
    nMonthFontThickness = 2
    nMonthTextMargin = 20*rMagnify
    nMonthW = ( (nRealSizeX + nMonthSpacing) / nNbrMonth ) - nMonthSpacing # nMonthSpacing: the last month spacing won't be rendered
    nMonthH = nRealSizeY
    #~ nMonthH = 50
    nStartYear = int(strStartDate[3:])
    for nNumMonth in range(nNbrMonth):
        x = nMargin+nNumMonth*(nMonthW+nMonthSpacing)
        y = nMargin
        drawRoundedRectangle( img, (x, y), (x+nMonthW, y+nMonthH), monthColor, 2, nCornerRadius, 0 )
        nCurrentNumMonth = nNumMonth + int(strStartDate[:2]) - 1
        strText = getMonthNameAbbrev( nCurrentNumMonth ) + (" %d" % (nStartYear+nCurrentNumMonth/12) )
        rScale, bl = getTextScaleToFit( strText, (nMonthW-nMonthTextMargin*2, 40), nMonthFont, nMonthFontThickness )
        cv2.putText( img, strText, (x+bl[0]+nMonthTextMargin,y+bl[1]+nMonthTextMargin), nMonthFont, rScale, monthColorText, nMonthFontThickness )

    #~ nNbrTaskLine = len(aListTask)
    #~ nTaskWidth = 30
    aTaskLineColor = [ (50, 255, 100), (50, 195,241), (120,76,125), (199, 133,62) ]
    taskColorText = (0, 0, 0)
    nTaskLineH = 48*rMagnify # was 50
    nTaskLineSpacing = 13*rMagnify # change here to have more or less spaces between each task line (was 20)
    nTaskFont = cv2.FONT_HERSHEY_SIMPLEX
    nTaskFontThickness = 2    
    nTaskTextMarginW = 0*rMagnify
    nTaskTextMarginH = 12*rMagnify
    nTaskSizeArrow = 40*rMagnify
    nTaskGroupMarginH = 30*rMagnify
    y = 40*rMagnify + nMargin + nMonthTextMargin - 20 # -40: remontes les barres plus pres des mois
    for nNumTaskLineGroup in range(len(aListTaskGroups)):
        for nNumTaskLine in range(len(aListTaskGroups[nNumTaskLineGroup])):
            y  += (nTaskLineH+nTaskLineSpacing)
            for nNumTask in range(len(aListTaskGroups[nNumTaskLineGroup][nNumTaskLine])):
                nArrowFlag = 3
                
                task = aListTaskGroups[nNumTaskLineGroup][nNumTaskLine][nNumTask]
                if len(task) < 1:
                    continue
                if( len(task) == 3 ):
                    task.append(nNumTaskLineGroup) # default color
                    
                strStartTask, rDuration, strText, nColorGroupIndex = task
                
                wTask = int(rDuration*nMonthW) + (int(rDuration+0.5)-1)*nMonthSpacing
                decayTime = getDurationInMonth(strStartDate, strStartTask)
                x = nMargin + int(decayTime * nMonthW)
                if( decayTime >= 1. ):
                    x += (int(decayTime+0.5)+0)*nMonthSpacing
                
                xRight = x+wTask-nTaskSizeArrow
                xText = x+bl[0]+nTaskTextMarginW+nTaskSizeArrow
                if( xRight > nSizeX - nMargin*2 - nTaskSizeArrow ):
                    xRight = nSizeX - nMargin*1
                    nArrowFlag = 2
                bCutLeft = False
                if( x < nMargin ):
                    wTask -= (-x-nMargin)-10
                    x = nMargin
                    nArrowFlag &= 1 # remove the 2 bit if set
                    bCutLeft = True
                print( "x: %s, xr: %s" % (x, xRight) )
                drawBigArrow( img, (x,y), (xRight, y+nTaskLineH), aTaskLineColor[nColorGroupIndex], 2, nTaskSizeArrow, 0, nArrowFlag = nArrowFlag )
                
                rScale, bl = getTextScaleToFit( strText, (wTask-nTaskTextMarginW*2-nTaskSizeArrow*2, nTaskLineH-nTaskTextMarginH*2), nTaskFont, nTaskFontThickness )
                print( "rScale: %s" % rScale )
                xText = x+bl[0]+nTaskTextMarginW+nTaskSizeArrow
                if( bCutLeft ):
                    xText = nMargin
                cv2.putText( img, strText, (xText,y+bl[1]+nTaskTextMarginH), nTaskFont, rScale, taskColorText, nTaskFontThickness )
        # for task line - end
        y += nTaskGroupMarginH
        
    # effacage du texte qui deborde
    cv2.rectangle( img, (nSizeX - nMargin,0),(nSizeX,nSizeY), (255,255,255),  -1 ) # -1 for full filled (cv2.CV_FILLED)
    
    # legends
    # up right
    xLegend = int(nSizeX*0.79)
    yLegend = int((nTaskLineH+nMargin)*rMagnify*1.7) # *1.2: modifier to move it down
    # bottom left
    xLegend = int(nSizeX*0.04)
    yLegend = int(nSizeY*0.9)
    
    nNumLegend = 0
    rScale /= 1.5
    nMarginLegend = int(20*rScale)
        
    if len(aLegends) > 0:
        nSizeBullet = int(12*rScale)
        nSizeBulletMargin = int(10*rScale)
        wText = 0
        hText = 0
        
        for txt in aLegends:
            rcRendered, baseline = cv2.getTextSize( txt, nTaskFont, rScale, nTaskFontThickness )
            print rcRendered
            if wText < rcRendered[0]:
                wText = rcRendered[0]+nSizeBullet
            if hText < rcRendered[1]:
                hText = rcRendered[1]
        cv2.rectangle( img, (xLegend-nMarginLegend, yLegend-nMarginLegend-1*hText), (xLegend+wText+nMarginLegend+nSizeBulletMargin, yLegend+(len(aLegends)-1)*hText*2+nMarginLegend), monthColorText, -1 )
    
        for txt in aLegends:
            cv2.rectangle( img, (xLegend,yLegend-hText/2-nSizeBullet/2),(xLegend+nSizeBullet,yLegend+nSizeBullet-hText/2-nSizeBullet/2), aTaskLineColor[nNumLegend], -1 )
            cv2.putText( img, txt, (xLegend+nSizeBullet+nSizeBulletMargin,yLegend), nTaskFont, rScale, aTaskLineColor[nNumLegend], nTaskFontThickness )
            yLegend += hText*2
            nNumLegend += 1
            
    # is legend - end
    
    return img
    
# renderRoadMap - end    

tl1 = [
                [ "07/2017", 1., "MM+EL+MB+JM: Grasp: SOA"],
                [ "08/2017", 3., "EL+MB+JM: Grasping: Scenario 1"],
                [ "11/2017", 3., "EL+MB+JM+NL: Grasping: Scenario 2"],
                
        ]
        
tl2 = [
                [ "07/2017", 3, "NL+AM: Adapted Pepper"],           
        ]        

tl3 = [
        ]       

tl4 = [  
        ]            
           
        
tl20 = [
                [ "07/2017", 8, "JM: Follow Audio Group"],
        ]              
tl21 = [
                [ "07/2017", 2, "EL: Launch Vision Group"],  
                [ "09/2017", 6, "EL: Follow Vision Group"],                  
        ]

tl22 = [
                [ "07/2017", 8, "MB/VP: Follow Semantic Group"],
                
        ]
        
tl23 = [    
                [ "07/2017", 8, "AM: Follow Navigation Progress"],
        ]

tl24 = [    
                [ "07/2017", 8, "AI Lab: Fundamental Research on Developmental Robotics"],
        ]
        
tl25 = [    
                [ "07/2017", 8, "All: Collaborative Projects and future works specifications"],
        ]
        
tl30 = [

                [ "06/2017", 36., "VP: Social co-learning for personal robots"],
            ]
            
tl31 = [
                [ "01/2016", 36, "MM: Simple Activity Recognition (with static Pepper)"],
        ]            
        
tl32 = [
                [ "01/2016", 36, "MN: Localisation topologique de robots humanoides"],
        ]
        
tl33 = [
                [ "09/2017", 7., "?+?+?: Social Interactions"],
            ]       


tl40 = [
              
        ] 
tl41 = [
                
        ]         
tl42 = [
        ]         
        
        
        
taskGroup1 = [tl1, tl2]
taskGroup2 = [tl20,tl21,tl22,tl23,tl24,tl25]
taskGroup3 = [tl30,tl31,tl32,tl33]
taskGroup4 = [tl40,tl41,tl42]
#~ taskGroupList = [taskGroup1, taskGroup2,taskGroup3,taskGroup4]
taskGroupList = [taskGroup1, taskGroup2,taskGroup3]
legends = ["Main Task", "Background task", "PhD" ]
    
img = renderRoadMap( "07/2017", 7, taskGroupList, legends )

strWindowName = "roadmap"
cv2.namedWindow( strWindowName, 0 )
cv2.moveWindow( strWindowName, 0,0 )
cv2.resizeWindow( strWindowName, img.shape[1]/2,img.shape[0]/2 )
cv2.imshow( strWindowName, img )
cv2.waitKey(0)
cv2.imwrite( "/tmp2/roadmap.png", img )
