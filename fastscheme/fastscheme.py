# -*- coding: utf-8 -*-

#
# Mega fast and chool schema editor
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

def computePerimeter(shape):
    rDist = 0
    for i in range(len(shape)-1): # we don't add the distance between last and first
        rDist += geo.distance( shape[i], shape[(i+1)%len(shape)] ) # modulo in the case of we want the distance to first and last
    return rDist
    
def generateCircle( center, radius ):
    """
    return a list of point to draw a circle
    """
    nNbrPoint = 64
    shape = []
    for i in range( nNbrPoint+1 ):
        rRad = i*2.*math.pi/nNbrPoint
        shape.append( [ int(center[0] + radius*math.cos(rRad)), int(center[1] + radius*math.sin(rRad))  ] )
    return shape

class FastScheme:
    def __init__( self, nResolutionW, nResolutionH ):
        self.nResolutionW = nResolutionW # rendeing resolution, could and will be different than window size
        self.nResolutionH = nResolutionH
        # but for the moment, they are of the same size
        self.listPts = [] # a list of list of coord (one for each trace)
        self.listObject = [] # a list of object to render
        # we've got 4 types of figures: rect, circle, and rect_with_title
        self.listClosedFiguresRect = []
        self.listClosedFiguresRectTitle = []
        self.listClosedFiguresCirc = []
        self.listClosedFigures = [self.listClosedFiguresRect, self.listClosedFiguresRectTitle, self.listClosedFiguresCirc] # not owned
        
        # this is an image used for shape sorting: each inner shape will be paint with a specific color 
        # and then a direct piking from mouse pointing will tell us, if we're inside or outside...
        # index => index of shape
        # 0 .. 1023 => rect (actually 0 .. kNbrFiguresPerShapeStyle
        # 1024.. 2047 => rect with title
        # ...
        self.kNbrFiguresPerShapeStyle = 1024
        #self.sortbuf = numpy.zeros((nResolutionH,nResolutionW,1), numpy.uint16)
        self.repaintSortBuf()
        
        
        self.nGridSize = 20
        self.bMouseDown = False
        self.aMouseDownPos = []
        self.mutexMouse = mutex.mutex()
        
        self.shapeMoved = None # a shape currently moving with mouse

        self.strSaveFilename = "/tmp/fastscheme.dat"
        self.loadFromDisk()
        
    def __del__( self ):
        self.exit()
    
    def saveToDisk(self):
        print( "INF: FastScheme.saveToDisk: saving to '%s'" % self.strSaveFilename )
        file = open( self.strSaveFilename, "wt" )
        file.write( repr(self.listClosedFigures) )
        file.close()
        
    def loadFromDisk(self):
        try:
            file = open( self.strSaveFilename, "rt" )
            aList = file.read()
            file.close()
        except:
            return 0
            
        print( "INF: FastScheme.loadFromDisk: loading from '%s'" % self.strSaveFilename );        
        aList = eval(aList)
        idx = 0        
        self.listClosedFiguresRect = aList[idx]; idx +=1
        self.listClosedFiguresRectTitle = aList[idx]; idx +=1
        self.listClosedFiguresCirc = aList[idx]; idx +=1
        self.listClosedFigures = [self.listClosedFiguresRect, self.listClosedFiguresRectTitle, self.listClosedFiguresCirc] # not owned
        self.repaintSortBuf()
        
        print( "INF: FastScheme.loadFromDisk: at end: %s" % self.__str__() )
        return 1
        
    def exit( self ):
        print( "INF: FastScheme.exit: exiting..." );
        self.saveToDisk()
        
    def __str__( self ):
        strOut = ""
        strOut += "closed figures: %s\n" % (len(self.listClosedFigures[0])+len(self.listClosedFigures[1])+len(self.listClosedFigures[2]))
        strOut += "closed rect: %s\n" % (len(self.listClosedFiguresRect))
        strOut += "closed rect w title: %s\n" % (len(self.listClosedFiguresRectTitle))
        strOut += "closed circle: %s\n" % (len(self.listClosedFiguresCirc))
        strOut += "full list: \n%s\n" % str(self.listClosedFigures)
        return strOut
        
    def computeShapeBuffer( self ):
        pass
        
    def repaintSortBuf( self ):
        self.sortbuf = numpy.zeros((self.nResolutionH,self.nResolutionW,1), numpy.uint16)
        for j in range( len(self.listClosedFigures) ):
            for i in range( len(self.listClosedFigures[j]) ):
                center = geo.compute_shape_median(self.listClosedFigures[j][i])
                self.paintSortBuf( i+j*self.kNbrFiguresPerShapeStyle, center )
        
    def paintSortBuf( self, nFigID, center ):
        """
        fill the sort buffer with the right color ID
        """
        #print(dir(cv2))
        #cv2.floodFill( self.sortbuf, nFigID, center, 255 ) # todo: find right command
        cv2.circle( self.sortbuf, (center[0],center[1]), 40, (nFigID), 100 ) # temp sprout
        print( self.sortbuf[0,0] )
        print( self.sortbuf[center[1],center[0]] )
        pass
        
        
    def analyseShape( self, shape ):
        """
        analyse a new shape
        return 1 if closed shape
        """
        nRet = 0
        rPerimeter = computePerimeter( shape )
        print( "rPerimeter: %s" % rPerimeter )        
        rLastFirstDist = geo.distance( shape[0], shape[-1] )
        print( "rLastFirstDist: %s" % rLastFirstDist )
        bb = geo.computeBoudingBox( shape )
        print( "bb: %s" % bb )
        rSizeBB = geo.distance( bb[0], bb[1] )
        print( "rSizeBB: %s" % rSizeBB )
        cornerBB = [ [bb[0][0],bb[0][1]], [bb[1][0],bb[0][1]], [bb[1][0],bb[1][1]], [bb[0][0],bb[1][1]]  ]
        rDistToBB = geo.compute_distance_to_points( shape, cornerBB )
        print( "rDistToBB: %s" % rDistToBB )
        if( rLastFirstDist * 6 < rPerimeter ): # 8
            # nearly ClosedFigure            
            shape.append( shape[0] )
            center = geo.median( bb[0], bb[1] )            
            self.gridify( center )            
            if( rDistToBB < rSizeBB *0.4 ):
                print( "Rectangle!")
                shape = cornerBB
                shape.append(cornerBB[0])
                self.gridifyShape( shape )
                self.listClosedFiguresRect.append(shape[:])
                nFigID = len(self.listClosedFiguresRect) - 1
            else:
                print( "Circle!")
                radius = abs( bb[0][0]-center[0] )
                radius = ((radius+(self.nGridSize/2))/self.nGridSize)*self.nGridSize
                shape = generateCircle( center, radius )
                #self.gridifyShape( shape )
                self.listClosedFiguresCirc.append(shape[:])
                nFigID = len(self.listClosedFiguresCirc) - 1 + self.kNbrFiguresPerShapeStyle*2
            self.paintSortBuf( nFigID, center )
            nRet = 1
        print( "INF: FastScheme.analyseShape: at end: %s" % self.__str__() )
        return nRet
    # analyseShape - end
            
            

    def mouseDown(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
        self.bMouseDown = True
            
        if( self.sortbuf[y,x] != 0 ): # or len(self.listClosedFiguresRect)>1
            nFigID = self.sortbuf[y,x]            
            self.aMouseDownPos = [x,y]
            nShapeFamily = nFigID / self.kNbrFiguresPerShapeStyle
            nShapeIdx = nFigID % self.kNbrFiguresPerShapeStyle
            self.shapeMoved = self.listClosedFigures[nShapeFamily][nShapeIdx]
        else:
            self.listPts.append([])
            self._mouseMove( x, y )
        self.mutexMouse.unlock()

    def mouseUp(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)        
        self._mouseMove( x, y )        
        self.bMouseDown = False
        if( self.shapeMoved != None ):
            self.shapeMoved = None
            self.repaintSortBuf()
        else:
            if( self.analyseShape( self.listPts[-1] ) ):
                self.listPts = []
        self.mutexMouse.unlock()
        
    def _mouseMove( self, x, y ):
        """
        unarmored moveMove version
        """
        if( self.bMouseDown ):
            if( self.shapeMoved != None ):
                # moving shape
                geo.translate_shape(self.shapeMoved, [x-self.aMouseDownPos[0], y-self.aMouseDownPos[1]] )
                self.aMouseDownPos = [x,y]
            else:
                self.listPts[-1].append([x,y])
        
    def mouseMove(self, x, y ):
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)        
        self._mouseMove(x, y)
        self.mutexMouse.unlock()
            
    def gridify( self, pt ):
        pt[0] = ((pt[0]+(self.nGridSize/2))/self.nGridSize)*self.nGridSize
        pt[1] = ((pt[1]+(self.nGridSize/2))/self.nGridSize)*self.nGridSize                
        
    def gridifyShape( self, shape ):
        for pt in shape:
            self.gridify( pt )
        
    def addFakeMouseMovements( self, listlistPts ):
        """
        Simulate a mouse draing a list of shapes.
        - listlistPts: a list of list of points (one list per shape)
        """
        for listPts in listlistPts:
            self.mouseDown( listPts[0][0], listPts[0][1] )
            for pt in listPts[1:-1]:
                self.mouseMove( pt[0], pt[1] )    
            self.mouseUp( listPts[-1][0], listPts[-1][1] )
            
    def update( self ):
        pass
        
    def render( self, img ):
        """
        render in an image (already created)
        """
        while( not self.mutexMouse.testandset() ):
            time.sleep(0.01)
            
        img_h, img_w, nbrplane = img.shape
        img[::] = (255,255,255)
        bMouseDown = self.bMouseDown
        for i in range(len(self.listPts)):
            shape = self.listPts[i]
            if( bMouseDown and i == len(self.listPts)-1 ):
                bLastOne = 1
            else:
                bLastOne = 0
            pt1 = shape[0]
            #~ if( not bLastOne ):
                #~ self.gridify(pt1)
            
            for pt2 in shape[1:]:
#                if( not bLastOne ):
#                    self.gridify(pt2)
                cv2.line( img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), (255,0,0) )
                pt1 = pt2
        # for listPts - end
        
        for listFig in self.listClosedFigures:
            for fig in listFig:
                pt1 = fig[0]
                for pt2 in fig[1:]:
                    cv2.line( img, (pt1[0], pt1[1]), (pt2[0], pt2[1]), (255,0,0), 2 )
                    pt1 = pt2

        
        self.mutexMouse.unlock()
    # render - end
        
# class FastScheme - end

def runApp(initFakeListListPts = None):
    """
    initFakeListListPts: a list of list of points, see addFakeMouseMovements
    """
    nCptFrameFps = 0
    timeBeginFps = time.time()
    nNbrFrameToComputeFps = 100
    
    screenName = "fast_scheme"
    bSmallScreen = 1
    nSizeX = 2960;
    nSizeY = 2100;
    if( bSmallScreen ):    
        nSizeX /=2
        nSizeY /=2
        
    fast = FastScheme(nSizeX, nSizeY)
    if( initFakeListListPts != None ):
        fast.addFakeMouseMovements(initFakeListListPts)


    def on_mouse_event(event, x, y, flags, param):
        #print (x, y)
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONUP:
            fast.mouseUp( x, y )
        elif event == cv2.EVENT_LBUTTONDOWN:
            fast.mouseDown( x, y )
        elif event == cv2.EVENT_MOUSEMOVE: # and (flags & cv2.CV_EVENT_FLAG_LBUTTON) :
            fast.mouseMove( x, y )
    # on_mouse_event - end

    screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    cv2.namedWindow( screenName )
    cv2.setMouseCallback( screenName, on_mouse_event )
    while(True):
    
        # read user events (background)
        fast.render( screen )
        cv2.imshow( screenName, screen )
        nKey =  cv2.waitKey(1) & 0xFF;
        if( chr(nKey) == 'q' ):
            break;

    
        time.sleep(0.02) # 0.03
        
        # print fps
        nCptFrameFps += 1
        if( nCptFrameFps > nNbrFrameToComputeFps ):
            duration = time.time()-timeBeginFps
            rFps = 1./(duration/nCptFrameFps)
            print( "fps: %5.1f" % rFps )
            nCptFrameFps = 0
            timeBeginFps = time.time()       
    # while(True) - end
    # fast = None; # call del, why it doesn't call it automatically !?! (rtfm)
    fast.exit()
    print( "INF: runApp: finished..." )
# runApp - end

listlistPts = [[[468, 290], [462, 290], [459, 290], [456, 290], [453, 290], [451, 291], [448, 292], [445, 294], [443, 295], [441, 298], [438, 303], [432, 314], [428, 323], [425, 330], [423, 336], [422, 340], [420, 346], [420, 353], [420, 363], [420, 372], [420, 383], [423, 392], [426, 401], [432, 408], [438, 416], [445, 422], [453, 428], [462, 435], [472, 441], [483, 445], [494, 449], [506, 449], [518, 449], [526, 449], [535, 448], [542, 446], [550, 441], [557, 436], [566, 430], [574, 424], [579, 415], [581, 407], [581, 398], [581, 386], [578, 377], [573, 369], [567, 360], [560, 352], [555, 347], [550, 341], [547, 335], [543, 329], [538, 326], [533, 322], [528, 318], [522, 315], [517, 311], [512, 308], [508, 302], [503, 299], [500, 297], [497, 296], [495, 296], [493, 295], [492, 295], [491, 295], [490, 295], [489, 294], [489, 294], [487, 294], [487, 294], [487, 295], [488, 295], [488, 295], [468, 290]], [[760, 224], [760, 226], [761, 229], [761, 235], [761, 243], [761, 254], [762, 269], [766, 283], [768, 300], [770, 316], [770, 330], [772, 336], [772, 340], [772, 341], [772, 341], [772, 341], [773, 341], [773, 341], [774, 341], [785, 341], [789, 341], [795, 341], [800, 341], [804, 341], [808, 341], [813, 340], [818, 339], [824, 337], [834, 334], [845, 334], [855, 332], [865, 332], [875, 332], [881, 332], [888, 333], [893, 333], [897, 335], [901, 335], [904, 336], [907, 336], [909, 336], [912, 335], [912, 334], [912, 334], [916, 331], [917, 330], [917, 330], [918, 324], [918, 321], [918, 315], [918, 311], [918, 306], [919, 301], [919, 294], [921, 288], [922, 282], [922, 276], [922, 273], [922, 271], [922, 268], [922, 265], [922, 260], [922, 258], [922, 257], [922, 257], [922, 256], [922, 254], [922, 253], [922, 252], [922, 251], [922, 249], [921, 248], [921, 247], [920, 245], [920, 244], [920, 243], [920, 240], [920, 237], [920, 234], [920, 232], [920, 231], [919, 231], [919, 231], [919, 231], [919, 231], [919, 231], [913, 229], [911, 228], [908, 228], [905, 228], [901, 229], [897, 229], [891, 229], [888, 229], [883, 228], [878, 228], [872, 227], [868, 227], [864, 227], [861, 227], [856, 227], [851, 227], [847, 227], [842, 227], [839, 227], [835, 227], [832, 227], [829, 227], [826, 226], [822, 226], [818, 226], [814, 226], [811, 226], [810, 226], [808, 225], [806, 225], [803, 225], [800, 225], [797, 225], [795, 225], [792, 225], [789, 225], [788, 224], [787, 224], [786, 222], [785, 222], [784, 222], [783, 222], [782, 222], [781, 222], [781, 222], [780, 222], [775, 222], [774, 222], [773, 222], [773, 222], [773, 222], [773, 223], [773, 223], [760, 224]], [[801, 466], [801, 467], [801, 468], [801, 470], [802, 473], [802, 476], [802, 481], [803, 489], [804, 497], [805, 505], [807, 512], [808, 519], [809, 526], [810, 532], [810, 537], [811, 544], [811, 551], [812, 559], [812, 565], [813, 568], [813, 571], [814, 572], [814, 573], [815, 573], [815, 574], [816, 575], [817, 576], [819, 577], [820, 577], [823, 578], [828, 579], [834, 580], [841, 581], [852, 581], [864, 583], [878, 585], [892, 586], [906, 587], [918, 589], [929, 589], [936, 589], [940, 589], [943, 589], [945, 589], [946, 589], [947, 589], [947, 589], [947, 589], [951, 585], [952, 582], [953, 579], [953, 573], [956, 565], [958, 554], [961, 540], [962, 524], [964, 507], [964, 491], [964, 481], [964, 473], [964, 469], [964, 467], [963, 466], [963, 465], [962, 464], [962, 464], [962, 463], [962, 463], [962, 463], [960, 463], [959, 462], [956, 461], [952, 461], [948, 460], [942, 460], [936, 459], [928, 459], [920, 459], [910, 459], [899, 459], [891, 461], [881, 462], [872, 462], [863, 463], [856, 463], [850, 464], [844, 464], [839, 465], [836, 465], [834, 465], [833, 465], [831, 465], [830, 465], [829, 465], [826, 465], [823, 465], [820, 465], [818, 465], [815, 465], [813, 465], [811, 465], [810, 466], [808, 466], [808, 466], [807, 466], [807, 465], [807, 465], [801, 466]]]
runApp(listlistPts)
print( "finished..." )