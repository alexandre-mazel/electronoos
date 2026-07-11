import os

# commande sous windows
for i in range( 1, 256 ):
    ret = os.system( "ping 192.168.0.%d -w 1000 -n 1" % i )
    print( ret )
    if ret == 0:
        print( "*" * 80 )
        print( "Found someone !!!" )