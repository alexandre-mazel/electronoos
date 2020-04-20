import cv2

class CV2_Drawer:
    """
    handle all mouse handling to draw on a cv2 drawed image.
    eg:
    im = cv2.imread("toto.jpg")
    drawer = CV2_Drawer( im)
    while 1:
        if drawer.isFinished():
            break
        
    
    """
    def __init__( self, image, strWindowName = "CV2 Draw" ):
        self.listSegment = [] # list of all mouse drawed segment
        self.strWindowName = strWindowName
        cv2.imshow("lesson",im)
        cv2.setMouseCallback( strWindowName, on_mouse_event )
        cv2.waitKey(0)
        
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
    
    def renderOnImage( self, image ):
        """
        render last position on image
        """
        
# class Drawer - end

    #~ screen = numpy.zeros((nSizeY,nSizeX,3), numpy.uint8)
    #~ cv2.namedWindow( screenName )
    
    
    """
    On peut multiplier le numérateur et le dénominateur par un meme nombre sans changer la valeur de la
    fraction, donc 3/5 = 3*2/5*2 =  6/10 soit 0.6
    """