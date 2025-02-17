"""
Socket: server device <=> client computer

(c) A.Mazel for EnsadLab 2024-2025
"""

import socket
import time
import math

import sys
sys.path.append("../test_socket")
from socket_server import getTimeStamp, smartFormatSize

def uintToBytes( n ):
    length = math.ceil(math.log(n, 256))
    res = int.to_bytes( n, length=length, byteorder='big', signed=False )
    return res
    
def bytesToUInt( b ):
    int.from_bytes( b, byteorder='big', signed = False ) # for byteorder, we could also use sys.byteorder

strServerIP = "192.168.4.1"

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect( ( strServerIP, 8090 ) )

clientsocket.send( b'hello' )
print( "INF: waiting for answer (1)..." )
ret = clientsocket.recv( 32 )
print( "INF: ret (1): ", ret )

time_begin = time.time()
nbr_received = 0
nbr_sent = 0
nbr_exchange = 0
while 1:
    data = b'Motor1' + uintToBytes(200)
    clientsocket.send( data )
    nbr_sent += len(data)
    
    #~ print( "INF: waiting for answer..." )
    ret = clientsocket.recv( 32 )
    nbr_received += len(ret)
    ret0 = ret[0]
    #~ ret0 = bytesToUInt( ret[0] )
    
    nbr_exchange += 1
    
    #~ print( "INF: ret: %s, ret0: %d, 0x%x" % (ret,ret0,ret0) )
    
    if ret0 != 100:
        print( "INF: ret: %s, ret0: %d, 0x%x" % (ret,ret0,ret0) )
        print( "INF: answer should be 100 and is wrong!" )
        break
        
    duration = time.time() - time_begin
    if duration > 5:
        received = nbr_received / duration
        sent = nbr_sent / duration
        print( "%s: nbr_exchange: %.1f (%d), Sent: %sB, Received: %sB" % ( getTimeStamp(), nbr_exchange/duration, nbr_exchange, smartFormatSize(sent), smartFormatSize(received) ) )
        time_begin = time.time()
        nbr_exchange = 0
        nbr_received = 0
        nbr_sent = 0
        
    
    time.sleep(0.01) # 0.01 => 100 ordre et reception par sec
        
    
print( "INF: client disconnected" )