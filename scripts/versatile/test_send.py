import versatile
import sys
strServerIP = sys.argv[1] # enter your ip on command line
v = versatile.Versatile()
v.connect( strServerIP )
ret = v.set( "passable", 1 )
print( "ret: %s" % str(ret) )
ret = v.set( "passable", "1" )
print( "ret: %s" % str(ret) )

