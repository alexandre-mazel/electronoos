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

strServerIP = "192.168.4.1"   # sur AP
#~ strServerIP = "192.168.0.25" # sur Box

print( "INF: Connecting to '%s'" % strServerIP )
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect( ( strServerIP, 8090 ) )

clientsocket.send( b'Hello' )
print( "INF: waiting for answer (1)..." )
ret = clientsocket.recv( 32 )
print( "INF: ret (1): ", ret )

time_begin = time.time()
nbr_received = 0
nbr_sent = 0
nbr_exchange = 0
while 1:
    data = b'Mot' + uintToBytes(200)
    if 1:
        # simulate 5 extra motors
        for i in range(5):
            data += uintToBytes(200+1+i)
            
    clientsocket.send( data )
    nbr_sent += len(data)
    
    if 1:
        # wait for the motor position
        #~ print( "INF: waiting for answer..." )
        ret = clientsocket.recv( 32 )
        nbr_received += len(ret)
        ret0 = ret[0]
        #~ ret0 = bytesToUInt( ret[0] )
        #~ print( "INF: ret: %s, ret0: %d, 0x%x" % (ret,ret0,ret0) )
        
        if ret0 != 100:
            print( "INF: ret: %s, ret0: %d, 0x%x" % (ret, ret0, ret0 ) )
            print( "INF: answer should be 100 and is wrong!" )
            break
            
    nbr_exchange += 1
        
    duration = time.time() - time_begin
    if duration > 5:
        received = nbr_received / duration
        sent = nbr_sent / duration
        print( "%s: nbr_exchange: %.1f (%d), Sent: %sB, Received: %sB" % ( getTimeStamp(), nbr_exchange/duration, nbr_exchange, smartFormatSize(sent), smartFormatSize(received) ) )
        time_begin = time.time()
        nbr_exchange = 0
        nbr_received = 0
        nbr_sent = 0
        
    
    time.sleep(0.004) # 0.01 => 100 ordre et reception par sec (mais ca va plus vite si on attend 2 fois moins)
        
    
print( "INF: client disconnected" )

"""
Stat 

*** Connection au client serveur MisBKit4 en AP depuis mstab7:

Best:
19h44m23: nbr_exchange: 6.2(31), Sent: 43.2B, Received: 6.165B

Puis en redressant l'ordi, j'ai eu mieux:
20h39m51: nbr_exchange: 44.5 (223), Sent: 311.3B, Received: 44.5B

# Real best: en optimisant un peu les tests et la boucle du python (et Motor => Mot)
23h52m16: nbr_exchange: 64.8 (324), Sent: 323.8B, Received: 64.8B


# juste en envoyant des donnees (pas de retour)
23h28m39: nbr_exchange: 65.3 (327), Sent: 326.3B, Received: 0.000B

*** connection au client serveur sur  MisBKit4 sur Freebox depuis mstab7:
# (pas de retour)
23h32m25: nbr_exchange: 65.7 (329), Sent: 328.4B, Received: 0.000B



When no connection:
Reponse de 192.168.4.1: octets=32 temps=191 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=228 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=58 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=398 ms TTL=64
"""