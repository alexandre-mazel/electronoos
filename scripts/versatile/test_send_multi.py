# sent value for 10 sec
import versatile
import sys
import time
strServerIP = sys.argv[1] # enter your ip on command line
v = versatile.Versatile()
v.connect( strServerIP )
for i in range( 10 ):
    ret = v.set( "passable", 1 )
    print( "ret: %s" % str(ret) )
    time.sleep(1.)
