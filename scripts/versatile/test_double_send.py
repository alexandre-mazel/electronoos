import versatile
import sys
strServerIP = sys.argv[1] # enter your ip on command line
v = versatile.Versatile()
v.connect( strServerIP )
ret = v.set( "passable", 1 )
print( "ret1: %s" % str(ret) )
ret = v.set( "passable", "1" )
print( "ret2: %s" % str(ret) )

v2 = versatile.Versatile()
v2.connect( strServerIP )

ret = v.set( "passable", "1" )
print( "ret3: %s" % str(ret) )

ret = v2.set( "passable2", "2" )
print( "ret3: %s" % str(ret) )

ret = v2.get( "passable2" )
print( "ret4: %s" % str(ret) )

ret = v.get( "passable" )
print( "ret5: %s" % str(ret) )
