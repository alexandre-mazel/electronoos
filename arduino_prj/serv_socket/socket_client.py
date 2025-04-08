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

bGraph = 0
bGraph = 1 # from 30fps to 10fps (with no real orders) from 5 to 4 with orders
# updating one over 4 frames: from 30fps to 20fps
# updating one over 10 frames: from 30fps to 25fps

if bGraph: 
    import graph_motor
    graph_motor.create_graph()

def uintToBytes( n ):
    if n == 0:
        length = 1
    else:
        length = math.ceil(math.log(n, 256)) # length in bytes
    res = int.to_bytes( n, length=length, byteorder='big', signed=False )
    return res
    
def sintToBytes( n ):
    if n == 0:
        length = 1
    else:
        length = math.ceil(math.log(abs(n*2), 256)) # length in bytes; *2 for the signed
    #~ print("DBG: sintToBytes: n: %d, length: %d" % (n,length) )
    res = int.to_bytes( n, length=length, byteorder='big', signed=True )
    #~ print("DBG: sintToBytes: returning (2): %s (len:%s)" % (res,len(res) ) )
    return res
    
def bytesToUInt( b ):
    #~ print("DBG: bytesToUInt: b: %s" % (b) )
    if isinstance(b,int):
        #~ print("DBG: bytesToUInt: is int!" )
        if b < 128:
            return b
        return b - 256
    res = int.from_bytes( b, byteorder='big', signed = True ) # for byteorder, we could also use sys.byteorder
    #~ print("DBG: bytesToUInt: returning (2): %s" % res )
    return res
if 1:
    assert bytesToUInt( 127 ) == 127, "erreur bytesToUInt: 127"
    assert bytesToUInt( 0x81 ) == -127, "erreur bytesToUInt: 0x81"
    assert bytesToUInt( b'\x81' ) == -127, "erreur bytesToUInt: b0x81"
    
    
def sendAndReceiveOrder( strServerIP ):
    
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
    """
    Format of a moteur order:
    'Mot' then for each motor: 1 byte of command and 1 byte of parameter.
    Command: 
    - 'P': position
    - 'S': speed
    - 'I': change ID (NDEV)

    Parameter:
    - Seen as signed char: -128..127 (both for position or speed)
    """
    nSimulatedMotorPos = 0
    bVerbose = 0

    while 1:
        data = b'Mot'
        if 0:
            data += uintToBytes(200)
            if 1:
                # simulate 5 extra motors
                for i in range(5):
                    data += uintToBytes(200+1+i)
        else:
            for i in range(6):
                if 0:
                    data += b'P' # for a Position order => 5.5fps
                elif 0:
                    data += b'V' # for a Velocity order (if velocity compute everything, but don't send it => 10fps)
                else:
                    data += b'F' # for a Fake order (do nothing) => 30fps
                value_order =  (nSimulatedMotorPos%255)-127
                data += sintToBytes(value_order)
                if bGraph: graph_motor.add_graph_order(i,value_order)
                
            nSimulatedMotorPos += 1
            
                
        if bVerbose: print("DBG: Sending data len(%d): %s" % (len(data),data) )
        clientsocket.send( data )
        nbr_sent += len(data)
        
        if 1:
            # wait for the motor position
            #~ print( "INF: waiting for answer..." )
            
            ret = clientsocket.recv( 32 )
            nbr_received += len(ret)
            if bVerbose: print( "INF: ret: %s" % (ret) )
            
            bSimulatedPosition = False
            if bSimulatedPosition:        
                ret0 = ret[0]
                ret0 = bytesToUInt( ret[0] )
                if bVerbose: print( "INF: ret: %s, ret0: %d, 0x%x" % (ret,ret0,ret0) )
                
                if ret0 != 100:
                    print( "INF: answer should be 100 and it's not!" )
                    break
            else:
                
                if ret[0:3] == b'Pos':
                    # We receive 6 motor pos
                    
                    bOutputOneLineFor6 = 1
                    bOutputOneLineFor6 = 0
                    
                    ret = ret[3:]
                    for i in range(len(ret)):
                        val = bytesToUInt( ret[i] )
                        if bGraph: graph_motor.add_graph_pos(i,val)
                        if bVerbose: print( "INF: val%d: %s, %d, 0x%x" % (i,val,val,val) )
                        if bOutputOneLineFor6: print(str(val) + ", ",end="")
                    if bOutputOneLineFor6: print("")
                    
                    
                    
                
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
            
            
        if bGraph: graph_motor.refresh_render()
        
        #~ time.sleep(0.004) # 0.01 => 100 ordre et reception par sec (mais ca va plus vite si on attend 2 fois moins)
        time.sleep(0.00001) # si c'est deja assez lent, ca sert a rien d'attendre ici
            
        if bVerbose: time.sleep( 5 ) # to help debugging
        
    print( "INF: client disconnected" )

    
strServerIP = "192.168.4.1"   # sur AP
#~ strServerIP = "192.168.0.25" # sur Box

sendAndReceiveOrder( strServerIP )

"""
Stat 

*** Connection au client serveur MisBKit4 en AP depuis mstab7:

Best:
19h44m23: nbr_exchange: 6.2(31), Sent: 43.2B, Received: 6.165B

Puis en redressant l'ordi, j'ai eu mieux:
20h39m51: nbr_exchange: 44.5 (223), Sent: 311.3B, Received: 44.5B

# Real best: en optimisant un peu les tests et la boucle du python (et Motor => Mot)
# even when Netflix running on the side (but not the same wifi nor channel)
# no Netflix change nothing
23h52m16: nbr_exchange: 64.8 (324), Sent: 323.8B, Received: 64.8B


# juste en envoyant des donnees (pas de retour)
23h28m39: nbr_exchange: 65.3 (327), Sent: 326.3B, Received: 0.000B

*** connection au client serveur sur  MisBKit4 sur Freebox depuis mstab7:
# (pas de retour)
23h32m25: nbr_exchange: 65.7 (329), Sent: 328.4B, Received: 0.000B
# pas mieux



When no connection:
Reponse de 192.168.4.1: octets=32 temps=191 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=228 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=58 ms TTL=64
Reponse de 192.168.4.1: octets=32 temps=398 ms TTL=64

# au final, en envoyant 5 val mot et retour 5 val mot
# MisBKit4 server, mstab7 client: 
12h58m22: nbr_exchange: 61.5 (308), Sent: 553.9B, Received: 369.3B

# XIAO_C3-1 server, mstab7 client:
12h55m34: nbr_exchange: 60.9 (305), Sent: 547.9B, Received: 365.3B
NB: en redressant l'ordi ca fonctionne moins bien

# XIAO_S3-1 server, mstab7 client:
14h32m28: nbr_exchange: 54.6 (274), Sent: 491.8B, Received: 327.9B
# pas mieux
"""

# scan for best channel automatic ?
# led qui dit connect et recois un paquet (clignote)
# lcd pour afficher l'ordi connecte :)
# bien d'etre seul a pouvoir se connecter!