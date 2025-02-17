"""
Socket: server device <=> client computer

(c) A.Mazel for EnsadLab 2024-2025
"""

import socket
import time
import math

def uintToBytes( n ):
    length = math.ceil(math.log(n, 256))
    res = int.to_bytes( n, length=length, byteorder='big', signed=False )
    return res
    
def bytesToUInt( b ):
    int.from_bytes(b, byteorder='big', signed = False ) # for byteorder, we could also use sys.byteorder

strServerIP = "192.168.4.1"

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect( ( strServerIP, 8090 ) )

clientsocket.send( b'hello' )
print( "INF: waiting for answer (1)..." )
ret = clientsocket.recv( 32 )
print( "INF: ret (1): ", ret )

while 1:
    clientsocket.send( b'Motor1' + uintToBytes(200) )
    print( "INF: waiting for answer..." )
    ret = clientsocket.recv( 32 )
    print( "INF: ret: ", ret, "0x%x" % ret )
    time.sleep(0.1)
    
print( "INF: client disconnected" )