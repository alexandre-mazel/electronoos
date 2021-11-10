import sys
sys.path.append( "../versatile" )
import versatile
strServerIP = sys.argv[1] # enter your ip on command line
v = versatile.Versatile()
v.connect( strServerIP )
ret = v.set( "breath", 1 )
