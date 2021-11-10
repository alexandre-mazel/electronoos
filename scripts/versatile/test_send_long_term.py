import time

import versatile
strServerIP = "localhost"
v = versatile.Versatile()
v.connect( strServerIP, bPatientMode=True )

while 1:
    print("------------ get -------------" )
    ret = v.set( "passable", 1 )
    print( "set, ret: %s" % str(ret) )
    time.sleep(1)
    print("------------ set -------------" )
    ret = v.get( "passable" )
    print( "get, ret: %s" % str(ret) )
    nTimeToWait = 5
    for i in range(nTimeToWait):
        print( nTimeToWait-i )
        time.sleep(1)
    print( 0 )
