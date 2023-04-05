import cv2 # >= cv 3.3.0
import numpy as np
import os
import sys
import time

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
print("strLocalPath: " + strLocalPath)

def isSameArray(a,b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True

global_count_check = 0
def checkArray(v1,v2):
    global global_count_check
    global_count_check += 1
    bEqual = isSameArray(v1,v2)
    if bEqual:
        print( "%s: GOOD: %s == %s" % (global_count_check,str(v1),str(v2) ) )
        return
    print( "%s: BAD: %s != %s" % (global_count_check,str(v1),str(v2) ) )
    assert(0)
    return
    
def union(a, b):
    x1 = min(a[0],b[0])
    y1 = min(a[1],b[1])
    x2 = max(a[2],b[2])
    y2 = max(a[3],b[3])
    
    return [x1,y1,x2,y2]
    
def intersection(a, b):
    x1 = max(a[0],b[0])
    y1 = max(a[1],b[1])
    x2 = min(a[2],b[2])
    y2 = min(a[3],b[3])
    
    if x2<=x1 or y2<=y1:
        return [0,0,0,0]
    
    return [x1,y1,x2,y2]

    
def areaSquarred(a):
    return (a[2]-a[0])*(a[3]-a[1])
    
def similarity(a,b):
    """
    return the cost (difference) between two rect
    """
    # compute the area of intersection/ area of union
    return areaSquarred(intersection(a,b))/areaSquarred(union(a,b))

def associateRects(listRect1,listRect2):
    """
    find the best combination to match rect in list2 to the one in list1.
    return for each rect in rect2 their index in list1.
    return -1 if it seems like a new rect
    """
    from sklearn.neighbors import KNeighborsClassifier
    import numpy as np
    classes = np.arange(len(listRect1))
    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(listRect1,y=classes)
    r = knn.predict(listRect1)
    if 0:
        # internal test
        print(r)
        assert(isSameArray(r,range(len(listRect1))))
    r = knn.predict(listRect2)
    if len(listRect1)>=len(listRect2):
        print("INF: associateRects: %s" % r)
    else:
        print("INF: associateRects: before kill: %s" % r)
        # two or more are pointing the same or sames
        simiTable = [0]*len(listRect2)
        for i in range(len(listRect2)):
            c = similarity(listRect2[i],listRect1[r[i]])
            simiTable[i] = c
        print("DBG: associateRects: costTable: %s" % simiTable )
        j = 0
        while j < len(r):
            # find other pointer to r[j]
            if r[j] != -1:
                i = 0 # on pourrait commencer a j+ 1 ?
                while i < len(r):
                    if i != j:
                        if r[i] == r[j]:
                            if simiTable[i] < simiTable[j]:
                               r[i] = -1
                            else:
                                r[j] = -1
                                break
                    i += 1
            j += 1
        print("INF: associateRects: %s" % r)

    return r
    
def testAssociateRects():
    lr1 = [
                [100,1000,200,1100],
                [500,1000,700,1200],
                [500,2000,700,2200],
                [500,2000,520,2020],
                [100,1000,1100,2100],
            ]
            
    lr2 = [
                [100,1000,1100,2100], # 4
                [500,2000,700,2200], # 2
                [100,1000,200,1100], # 0
                [500,1000,700,1200], # 1
                [500,2000,520,2020], # 3
            ]
            
    lr3 = [
                [100,1000,1100,2100], # 4
                [9500,92000,9700,92200], # 2 is very different
                [100,1000,200,1100], # 0
                [500,1000,700,1200], # 1
                [500,2000,520,2020], # 3
            ]
            
    lr4 = [
                [100,1000,1100,2100], # 4
                # 2 is missing
                [100,1000,200,1100], # 0
                [500,1000,700,1200], # 1
                [500,2000,520,2020], # 3
            ]
            
    lr5 = [
                [100,1000,1100,2100], # 4
                [500,2000,700,2200], # 2
                [100,1000,200,1100], # 0
                [500,1000,700,1200], # 1
                [500,2000,520,2020], # 3
                [600,2100,620,2120], # a new one: 5
            ]


    associateRects(lr1,lr2) # time for init
    
    timeBegin = time.time()
    
    r = associateRects(lr1,lr2)
    checkArray(r, [4,2,0,1,3])
    
    r = associateRects(lr1,lr3)
    checkArray(r, [4,2,0,1,3])
    
    r = associateRects(lr1,lr4)
    checkArray(r, [4,0,1,3])
    
    r = associateRects(lr1,lr5)
    checkArray(r, [4,2,0,1,3,-1])

    
    print("duration: %.3fs" % (time.time()-timeBegin))
    exit(0)
    
testAssociateRects()


def findCloser( listFaceResult, rect, confidence_treshold = 0.13 ):
    """
    find in listFaceResult the closer rect with rect.
    Return intersection_rect, matching_rect, ratio_intersection, confidence_of_matching_rect
    or [] if no intersection
    - rect: a rect (startX, startY, endX, endY)
    """
    #~ print("DBG: findCloser: looking to match %s" % str(rect) )
    rScoreMax = 0
    best = [] # intersection and original rect
    sx,sy,ex,ey = rect
    area_1 = (ex-sx)*(ey-sy)
    for oneres in listFaceResult:
        sx,sy,ex,ey = rect
        rsx, rsy, rex, rey, confidence = oneres
        if confidence <= confidence_treshold:
            continue
        area_2 = (rex-rsx)*(rey-rsy)
        if rsx > sx: sx = rsx
        if rsy > sy: sy = rsy
        if rex < ex: ex = rex
        if rey < ey: ey = rey
        if sx>=ex or sy>=ey:
            continue
        inter_area = (ex-sx)*(ey-sy)
        ratio_inter = inter_area / ((area_1+area_2)/2)
        #~ print("DBG: findCloser: rect: %s, inter_area: %d, ratio_inter: %.1f" % (str(oneres[:4]), inter_area, ratio_inter ) )
        if rScoreMax < ratio_inter:
            rScoreMax = ratio_inter
            best = (sx,sy,ex,ey), (rsx, rsy, rex, rey), ratio_inter, confidence
        
    print("DBG: findCloser: returning: %s" % str(best) )
    return best
    
if 0:
    listRes = [
    (0,0,100,200,0.5),
    (25,35,40,60,0.6),
    ]

    res = findCloser( listRes, (20,40,40,60) )
    print("findBestIntersection: %s" % str(res) )
    
def selectFace( faces_list, img_shape ):
    """
    select a list of face by returning the biggest and most centered
    - faces_list: from detector
    - img_shape: shape object (h,w,[layer]) from opencv image
    """
    if len(faces_list) < 1:
        return []
    h = img_shape[0]
    w = img_shape[1]    
    nMaxScore = -1024*1024*1024; # INT_MIN
    nIdxBest = -1;
    print(faces_list)
    for i in range(len( faces_list ) ):
        xt, yt, xb, yb,rConf = faces_list[i]
        facew = xb-xt;
        faceh = yb-yt;        
        nScore = 0; # all distances are compared in square
        nScore += facew*faceh*8; # *8: it's a parameter to make the size weight "more quite the same" compared to the distance
        dx = ( w / 2 ) - ( xt + (facew/2) );
        dy = ( h / 2 ) - ( yt + (faceh/2) );
        nScore -= dx*dx+dy*dy;
        print( "DBG: FaceDetectionNew_select_face: i:%d, score: %s" % (i,nScore) )
        if( nScore > nMaxScore ):
            nMaxScore = nScore;
            nIdxBest = i;
            
    # now the best is in idx...
    return faces_list[nIdxBest]
# FaceDetectionNew_select_face - end

class FaceDetector:
    """
    detect face using dnn included in cv3 since the 3.3.0
    """
    
    def __init__( self ):
        self.load()
        
    def load( self ):
        # load coffee models
        print( "ING: FaceDetectorCV3: Loading face models" )
        strPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ strPath = "/home/pi/dev/git/electronoos/alex_pytools/"
        if strPath == "": strPath = '.'
        strPath += "/../models/"
        strProtoTxt = strPath + "facedetect_deploy.prototxt.txt"
        strModel = strPath + "facedetect_res10_300x300_ssd_iter_140000.caffemodel"
        self.net = cv2.dnn.readNetFromCaffe( strProtoTxt, strModel )
        
    def render_res( self, im, res, color = (255,0,0), bRenderAll = False ):
        """
        render result from a previous analyse in im
        return im (as given)
        """
        for oneres in res:
            startX, startY, endX, endY, confidence = oneres
            #~ print("DBG: render_res: confidence: %s" % confidence )
            col = color
            if confidence < 0.5:
                col = (col[0]//2,col[1]//2,col[2]//2)
            if confidence < 0.25:
                col = (col[0]//2,col[1]//2,col[2]//2)
            if confidence < 0.14 and not bRenderAll:
                continue
            cv2.rectangle( im, (startX,startY), (endX, endY), col )
            # etiquette and confidence
            cv2.rectangle(im,(startX, startY-14),(startX+40, startY), col, thickness=-1 )
            cv2.putText(im,"%.2f"%confidence,(startX+2, startY-2),cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(255,255,255), thickness = 1 )
        return im
        
    def detect( self, im, bRenderBox = True,confidence_threshold = 0.5, bRenderAll = False ):
        """
        return a list of face: x_start, y_start, x_end, y_end
        """
        
        if len(im.shape)==2 or im.shape[2] == 1: 
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        blob = cv2.dnn.blobFromImage( im, 1.0, (300, 300), (104.0, 177.0, 123.0) )
        h,w,n=im.shape
        print("DBG: detect: src is %dx%dx%d" % (w,h,n) )

        print("DBG: computing face detections...")
        timeBegin = time.time()
        self.net.setInput(blob)
        detections = self.net.forward()
        #~ print("INF: detections: %s\n" % (str(detections)))
        print("INF: analyse takes: %5.2fs\n" % (time.time()-timeBegin))
        res = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                if startX >= w-6 or startY >= h-6:
                    continue # face is out of screen,(or very small), weird, let's remove it
                res.append((startX, startY, endX, endY, confidence))
                #~ print("DBG: box: %s" % str(box))
                #~ print("DBG: x,y: %d,%d" % (startX, startY))
                
        if bRenderBox: self.render_res( im, res, bRenderAll=bRenderAll )
        return res
# class FaceDetector - end

facedetector = FaceDetector()

        
if __name__ == "__main__":
    im = cv2.imread("../data/girl_face.jpg")
    facedetector.detect(im)