import cv2
import numpy as np
import os
import sys

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

def updateCounter( sd, astrKeyPath, nInc = 1 ):
    """
    increment a counter in sd, a super dict: a dict of dict of dict... 
    - astrKeyPath is the list of key, eg ["monday", "alexandre", "hand washing"].
    NB: if the key doesn't exists, it will be created at 0.
    """
    d = sd
    for i in range( len(astrKeyPath) ):
        k = astrKeyPath[i]
        if k not in d.keys():
            if i == len(astrKeyPath)-1:
                d[k] = nInc
                return
            d[k] = dict()
        else:
            if i == len(astrKeyPath)-1:
                d[k] += nInc
                return
        d = d[k]
    assert(0)

    
    
def sumDict( sd ):
    """
    sum all values in a super dictionnary.
    eg: {'start': {'Alex': {'192.168.0.1': 30}, 'toto': 15 } will return 45
    """
    s = 0
    for k,v in sd.items():
        #~ print("k: %s" % str(k))
        if isinstance(v,dict):
            s += sumDict(v)
        else:
            s += v
    return s
    
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
    
    return rScale, ( (rectToFit[0]-rcRendered[0]) // 2, rectToFit[1]-(rectToFit[1]-rcRendered[1]) // 2 )
    
    
def renderBarGraph( im, dValue, lt, rb, rMaxValue = 100. ):
    """
    render in im a bargraph value for each value in dictValue, a value can be just a number or a dict of number (but not dict of dict)
    eg: {"day1": {"a1":12, "a2":25}, "day2": {"a2":30, "a3":12} } NB: rMaxValue is here 30
    - lt: left top position to start render the bargraph, rb: right bottom point
    """
    grey = (127,127,127)
    lgrey = (191,191,191)
    black = (0,0,0)
    colors = ( (255,0,0), (255,127,0), (255,0,127),(0,255,0), (127,255,0), (0,255,127) )
    nFont = cv2.FONT_HERSHEY_SIMPLEX
    nFontThickness = 1
    
    maxSubLen = 0
    for k,d in dValue.items():
        if len(d) > maxSubLen:
            maxSubLen = len(d)
            
    wMargin = 4
    wPerVal = ( rb[0]-lt[0]-wMargin ) / len(dValue)
    wPerSubVal = (wPerVal / maxSubLen) - 1
    
    hPerUnit = ( rb[1]-lt[1] ) / rMaxValue
    
    xGraph = lt[0]+wMargin
    hLegend = 20
    bottomValue = rb[1] - hLegend
    
    cv2.rectangle(im, lt, rb, grey, 1 )
    nCptH = 0
    for kh, vh in sorted(dValue.items()):
        if not isinstance(vh,dict):
            cv2.rectangle( im, (lt[0]+nCptH*wPerVal,rb[1]), (lt[0]+nCptH*wPerVal+wPerVal-1,rb[1]-vh*hPerUnit), colors[0], 0 )
        else:
            nCpt = 0
            for d,v in sorted(vh.items()):
                p1 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt), bottomValue  )
                p2 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt+wPerSubVal-wMargin ), int(bottomValue-v*hPerUnit) )
                cv2.rectangle( im,p1,p2, colors[nCpt], -1 )
                nCpt += 1
        p1 = (int( xGraph+nCptH*wPerVal), bottomValue )
        p2 = (int( xGraph+nCptH*wPerVal+wPerVal)-wMargin, rb[1] )
        
        cv2.rectangle( im, p1, p2, lgrey, 1 )
        rScale,offsettext = getTextScaleToFit(kh, (p2[0]-p1[0],p2[1]-p1[1]), nFont,nFontThickness)
        cv2.putText(im, kh, (p1[0]+offsettext[0],p1[1]+offsettext[1]), nFont, rScale, black, nFontThickness )
            
        nCptH += 1
        
# renderBarGraph - end

class Analytics:
    
    def __init__( self, strPostName = "" ):
        """
        - strPostName: used mainly for auto testing
        """
        self.strSaveFileName = os.path.expanduser("~/") + ("analytics%s.dat" % strPostName )
        self.dStatPerDay = dict() # for each day for each app name, for each event for each user id, for each ip then a counter 
        self.load()
        self.strDebugFakeDate = ""
        
    def __del__( self ):
        self.save()
        
        
    def save(self):
        f=open(self.strSaveFileName, "wt")
        f.write(repr((self.dStatPerDay,None)))
        f.close()
        
    def load(self):
        try:
            f=open(self.strSaveFileName, "rt")
            data = f.read()
            reconstructed = eval(data) # harsh unsafe!
            print("DBG: Analytics.load: loading: '%s'" % str(reconstructed) )
            self.dStatPerDay, dummy  = reconstructed
            f.close()  
        except BaseException as err:
            print("WRN: Analytics.load: %s" % str(err) )
            return
            
    def setDebugFakeDate( self, strNewFakeDate ):
        self.strDebugFakeDate = strNewFakeDate
            
    def update( self, strIP, strUserID, strAppName, strEvent ):
        strD = misctools.getDayStamp()
        if self.strDebugFakeDate != "":
            strD = self.strDebugFakeDate
        updateCounter(self.dStatPerDay, (strD, strAppName, strEvent, strUserID, strIP) )
        #~ print( "DBG: Analytics.update: data:\n" + str(self.dStatPerDay ) )
        
    def render( self, strDateStart = "1874_01_01", strDateStop = "9999_01_01" ):
        """
        return an image with the rendered statistics
        """
        white = (255,255,255)
        black = (0,0,0)
        blue = (255,0,0)
        w = 640
        h = 480
        img = np.zeros((h,w,3), np.uint8)
        img[:] = white
        
        # global per day
        dPerDay = dict()
        max = 0
        for kd,d in sorted(self.dStatPerDay.items()):
            if kd >= strDateStart and kd <= strDateStop:
                dPerDay[kd] = dict()
                for kapp,d in sorted(d.items()):
                    sum = sumDict(d)
                    if sum > max:
                        max = sum
                    dPerDay[kd][kapp] = sum
        renderBarGraph( img, dPerDay, (10, 10), (630, 470), max )
                
        
        
        return img
        
# class Analytics - end

def autoTest():
    a = Analytics("_test")
    
    strIP1 = "192.168.0.1"
    strIP2 = "192.168.0.2"
    strIP3 = "192.168.0.3"
    u1 = "Alex"
    u2 = "JP"
    a1 = "boot"
    a2 = "telepresence"
    a3 = "detecthuman"
    a4 = "app4"
    a5 = "app5"
    a6 = "app6"
    e1 = "start"
    e2 = "stop"
    
    astrFakeDate = ["2020_07_01", "2020_07_02", "2020_07_03", "2020_07_04", "2020_07_05", "2020_07_06", "2020_08_01", "2020_09_02"]
    for i in range(8):
        a.setDebugFakeDate(astrFakeDate[i] )
        a.update( strIP1, u1, a1, e1 )
        a.update( strIP1, u1, a1, e2 )
        a.update( strIP1, u1, a1, e1 )
        a.update( strIP1, u1, a1, e2 )
        if i & 2:
            a.update( strIP1, u1, a2, e1 )
            a.update( strIP1, u1, a2, e1 )
            a.update( strIP3, u2, a5, e1 )
            a.update( strIP3, u2, a6, e1 )
        if i & 3:
            a.update( strIP1, u1, a2, e2 )
            a.update( strIP2, u1, a2, e1 )
            a.update( strIP3, u2, a2, e1 )
            a.update( strIP3, u2, a4, e1 )
        if i & 5:
            a.update( strIP1, u1, a2, e2 )
            a.update( strIP2, u1, a2, e1 )
            a.update( strIP3, u2, a2, e1 )
            a.update( strIP3, u2, a4, e1 )
            
    img = a.render()
    cv2.imshow("stat", img )
    cv2.waitKey(0)
    
# autoTest - end

if __name__ == "__main__":
    autoTest()

        
        
        
        
        
        