import cv2
import sys
import time
sys.path.append( "../versatile" )
from versatile import Versatile

def showBroadcast(strIP, strBroadcasterID):
    strBroadcasterID = str(strBroadcasterID) # assume string
    nPort = 15000
    v = Versatile( nPort )
    v.connect( strIP )
    #~ v.setVerbose(True)
    
    nCptImage = 0
    timeBegin = time.time()
    while 1:
        print("looping...")
        vi, cvim = v.getBrodcastedImage(strBroadcasterID)
        if not cvim is None:
            strTxt = "%ds%03d" % ( vi.timeStamp[0],vi.timeStamp[1] )
            print( strTxt )
            cv2.putText( cvim, strTxt, (10, 10 ), 0, 0.5, (255,255,255) )
            cv2.imshow(strBroadcasterID,cvim)
            cv2.waitKey(1)
        else:
            print( "ERR in get image" )

        nCptImage += 1
        if nCptImage>100:
            rDuration = time.time() - timeBegin
            print( "INF: fps: %5.2fim/s" % (nCptImage/rDuration) )
            timeBegin = time.time()
            nCptImage = 0
        time.sleep( 0.03 )
# showBroadcast - end

if len( sys.argv ) < 3:
    print( "syntax: scriptname ip broadcaster_id" )

#~ showBroadcast("localhost", 1657163486)
showBroadcast(sys.argv[1], sys.argv[2] )