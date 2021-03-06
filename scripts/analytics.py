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

def maxDict( sd ):
    """
    get max of all values in a super dictionnary.
    eg: {'start': {'Alex': {'192.168.0.1': 30}, 'toto': 15 } will return 45
    """
    s = -1000
    for k,v in sd.items():
        if isinstance(v,dict):
            s = max( s, maxDict(v) )
        else:
            s = max(s,v)
    return s
    
def getTextScaleToFit( strText, rectToFit, fontFace, nThickness = 1 ):
    """
    Compute the biggest scale to fit in some rectangle
    - rectToFit: a pair (w,h)
    return [rScale, tl_to_center]
        - rScale: scale to render
        - tl_to_center: the bottom left point to render the font in the rectToFit for the font to be centered
    """
    #~ print("DBG: getTextScaleToFit: txt: '%s', rectToFit: %s" % ( str(strText), str(rectToFit) ) )
    rScale = 2.
    while( rScale > 0. ):
        rcRendered, baseline = cv2.getTextSize( strText, fontFace, rScale, nThickness )
        #~ print("rendered: %s" % str(rcRendered) )
        if( rcRendered[0] < rectToFit[0] and rcRendered[1] < rectToFit[1] ):
            break
        rScale -= 0.1
        #~ print("rScale: %s" % rScale )
    
    return rScale, ( (rectToFit[0]-rcRendered[0]) // 2, rectToFit[1]-(rectToFit[1]-rcRendered[1]) // 2 )
    
def renderVerticalText( im, txt, p1, p2, color ):
    """
    render a text in a vertical rectangle, compute letter size based on space
    """
    nFont = cv2.FONT_HERSHEY_SIMPLEX
    nFontThickness = 1
    w = p2[0] - p1[0]
    h = p2[1] - p1[1]
    rScaleMin = 100
    #~ print(w,h)
    for c in txt:
        rScale, offsettext = getTextScaleToFit( c, (w,int(h/(len(txt)*1.1)) ), nFont, nFontThickness )
        if rScaleMin>rScale: rScaleMin = rScale
      
    #~ print(rScaleMin)

    #~ rcLetterMax = [0,0]
    #~ for c in txt:
        #~ rcLetter, baseline = cv2.getTextSize( c, nFont, rScaleMin, nFontThickness )
        #~ if rcLetterMax[0]<rcLetter[0]: rcLetterMax[0]=rcLetter[0]
        #~ if rcLetterMax[1]<rcLetter[1]: rcLetterMax[1]=rcLetter[1]
    
    #~ print("DBG: rcLetterMax: %s"%str(rcLetterMax) )    
    
    yLetter = p1[1] + 2
    for i,c in enumerate(txt):
        rcLetter, baseline = cv2.getTextSize( c, nFont, rScaleMin, nFontThickness )
        cv2.putText(im, c, (int(p1[0]+(w-rcLetter[0])//2),yLetter+rcLetter[1]), nFont, rScaleMin, color, nFontThickness )
        if 0:
            # letters spread on all height
            hPerLetter = h//len(txt) # (offsettext[1]*2)
            yLetter += hPerLetter
        else:
            yLetter += rcLetter[1] + int(8*rScaleMin) # (rcLetterMax[1]*1.5
            
def renderCenteredText( im, txt, p1, p2, color, nFont, nFontThickness ):
    rScale,offsettext = getTextScaleToFit(txt, (p2[0]-p1[0],p2[1]-p1[1]), nFont,nFontThickness)
    cv2.putText(im, txt, (p1[0]+offsettext[0],p1[1]+offsettext[1]), nFont, rScale, color, nFontThickness )

def renderBarGraph( im, dValue, lt, rb, rMaxValue = -1 ):
    """
    render in im a bargraph value for each value in dictValue, a value can be just a number or a dict of number (but not dict of dict)
    eg: {"day1": {"a1":12, "a2":25}, "day2": {"a2":30, "a3":12} } NB: rMaxValue is here 30
    - lt: left top position to start render the bargraph, rb: right bottom point
    - rMaxValue: pass max value if known, else it will be recomputed
    """
    grey = (127,127,127)
    lgrey = (191,191,191)
    black = (0,0,0)
    white = (255,255,255)
    colors = ( (255,0,0), (255,127,0), (255,0,127),(0,255,0), (127,255,0), (0,255,127) )
    nFont = cv2.FONT_HERSHEY_SIMPLEX
    nFontThickness = 1
    
    if rMaxValue == -1:
        #compute max value!
        rMaxValue = maxDict(dValue)
    
    maxSubLen = 0
    for k,d in dValue.items():
        if isinstance(d,dict):
            nSub = len(d)
        else:
            nSub = 1        
        if nSub > maxSubLen:
            maxSubLen = nSub
            
    wMargin = 4
    hLegend = 20
    hNumber = hLegend//2
    wPerVal = ( rb[0]-lt[0]-wMargin ) / len(dValue)
    wPerSubVal = (wPerVal / maxSubLen) - 1
    
    hPerUnit = ( rb[1]-lt[1]-hLegend-wMargin-hNumber ) / rMaxValue
    
    xGraph = lt[0]+wMargin
    bottomValue = rb[1] - hLegend
    
    #~ cv2.rectangle(im, lt, rb, lgrey, 1 )
    nCptH = 0
    for kh, vh in sorted(dValue.items()):
        if not isinstance(vh,dict):
           # cv2.rectangle( im, (lt[0]+nCptH*wPerVal,rb[1]), (lt[0]+nCptH*wPerVal+wPerVal-1,rb[1]-vh*hPerUnit), colors[0], 0 )
            nCpt = 0
            v = vh
            p1 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt), int(bottomValue-v*hPerUnit) )
            p2 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt+wPerSubVal-wMargin ), bottomValue )
            cv2.rectangle( im,p1,p2, colors[nCptH%len(colors)], -1 )
            renderCenteredText( im, str(v), (p1[0],p1[1]-hNumber), (p2[0],p1[1]-1), black, nFont, nFontThickness )
            
        else:
            nCpt = 0
            for d,v in sorted(vh.items()):
                p1 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt), int(bottomValue-v*hPerUnit) )
                p2 = (int( xGraph+nCptH*wPerVal+wPerSubVal*nCpt+wPerSubVal-wMargin ), bottomValue )
                cv2.rectangle( im,p1,p2, colors[nCpt%len(colors)], -1 )
                renderVerticalText( im, d, p1, p2, white )
                renderCenteredText( im, str(v), (p1[0],p1[1]-hNumber), (p2[0],p1[1]-1), black, nFont, nFontThickness )
                
                nCpt += 1
        p1 = (int( xGraph+nCptH*wPerVal), bottomValue )
        p2 = (int( xGraph+nCptH*wPerVal+wPerVal)-wMargin, rb[1] )
        
        #~ cv2.rectangle( im, p1, p2, lgrey, 1 )
        renderCenteredText( im,kh,p1,p2, black, nFont,nFontThickness )
            
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
        
    def render( self, strDateStart = "1874_01_01", strDateStop = "9999_01_01", strRestrictToApp = None ):
        """
        return an image with the rendered statistics
        """
        white = (255,255,255)
        black = (0,0,0)
        blue = (255,0,0)
        w = int(640*1.9)
        h = int(480*1.6)
        w2=w//2
        h2=h//2
        img = np.zeros((h,w,3), np.uint8)
        img[:] = white
        
        # globalize per day and sum per apps
        dPerDay = dict()
        dPerApps = dict()
        dPerEv = dict()
        dPerUser = dict()
        dPerIP = dict()
        for kd,d in sorted(self.dStatPerDay.items()):
            if kd >= strDateStart and kd <= strDateStop:
                dPerDay[kd] = dict()
                for kapp,d in sorted(d.items()):
                    if strRestrictToApp != None and strRestrictToApp not in kapp:
                        continue
                    sum = sumDict(d)
                    dPerDay[kd][kapp] = sum
                    updateCounter( dPerApps,[kapp], sum)
                    
                    for kEv, d in sorted(d.items()):
                        for kUser, d in sorted(d.items()):
                            for kIP, d in sorted(d.items()):
                                updateCounter( dPerEv,[kEv], d)
                                updateCounter( dPerUser,[kUser], d)
                                updateCounter( dPerIP,[kIP], d)
                    
        renderBarGraph( img, dPerApps,  (10, 10),              (w2-10, h2-10) )
        renderBarGraph( img, dPerDay, (w2+10, 10),       (w-10, h2-10) )
        renderBarGraph( img, dPerEv,    (10, h2+10),        (w2-10, h-10) )                
        renderBarGraph( img, dPerUser, (w2+10, h2+10), (w-10, h-10) )
        
        return img
        
# class Analytics - end

def autoTest():
    a = Analytics("_test")
    
    strIP1 = "192.168.0.1"
    strIP2 = "192.168.0.2"
    strIP3 = "192.168.0.3"
    u1 = "Alex"
    u2 = "JP"
    a1 = "BOOT"
    a2 = "Telepresence"
    a3 = "DetectHumanMec"
    a4 = "app4"
    a5 = "app5"
    a6 = "app6"
    e1 = "start"
    e2 = "stop"
    
    astrFakeDate = ["2020_07_01", "2020_07_02", "2020_07_03", "2020_07_04", "2020_07_05", "2020_07_06", "2020_08_01", "2020_09_02"]
    for i in range(len(astrFakeDate)):
        a.setDebugFakeDate(astrFakeDate[i] )
        a.update( strIP1, u1, a1, e1 )
        a.update( strIP1, u1, a1, e2 )
        a.update( strIP1, u1, a1, e1 )
        a.update( strIP1, u1, a1, e2 )
        a.update( strIP1, u1, a3, e1 )
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
    
    img = a.render(strRestrictToApp="BOO")
    cv2.imshow("stat", img )
    cv2.waitKey(0)

    img = a.render(strRestrictToApp="Te")
    cv2.imshow("stat", img )
    cv2.waitKey(0)
    
# autoTest - end

if __name__ == "__main__":
    autoTest()

        
        
        
        
        
        