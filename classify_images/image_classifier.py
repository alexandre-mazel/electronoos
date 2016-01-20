import cv2
import os

def classifyPath( strPathSrc, strPathDest ):
        for file in os.listdir( strPathSrc ):
            strSrc = strPathSrc + "/" + file
            if( os.path.isdir( strSrc ) ):
                classifyPath( strSrc, strPathDest )
            else:
                print( "Reading: %s" % strSrc ),
                im = cv2.imread( strSrc )
                sy,sx,c = im.shape
                h = min(sy,sx)
                w = max(sy,sx)
                print( "w: %s, h: %s" % (w,h) ),
                if( w == 2496 and h == 1664 ):
                    print( "Canon" ),
                print( "" )



classifyPath( "/home/a/recup3/", "/tmp/classified/" )
