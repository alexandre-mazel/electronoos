import socket
import time
import datetime
import os

def getTimeStamp():
    """
    return (hour,min,second)
    """
    datetimeObject = datetime.datetime.now()
    return "%2dh%02dm%02d" % (datetimeObject.hour, datetimeObject.minute, datetimeObject.second)
    
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

num_port = 8090
sock.bind(('0.0.0.0', num_port ))
sock.listen(1)

print("INF: Serving socket on %s" % num_port )

total_data_received = 0

while True:
    client, addr = sock.accept()
    sock.settimeout(5) # kill if read received no information after 5 sec
    sock.setblocking(0)
    
    print("INF: %s: Client connected from %s..." % ( getTimeStamp(), str(addr) ) )
    
    nPrevData = 99
    
    time_begin = time.time()
    nbr_data_received = 0;
    while True:
        flags = 0
        if os.name != "nt":
            flags |= socket.SOCK_NONBLOCK
        content = client.recv(256,flags)

        if len(content) ==0:
           break
           
        print(content)
        for data in content:
            #~ print( "0x%x" % data )
            if not ( data == nPrevData+1 or (data == 0 and nPrevData == 99) ):
                print("ERR: data corrupted (data: %d, nPrevData: %d)" % (data,nPrevData) )
                client.recv(4096) # flush all
                break
            nPrevData = data
        else:
            # normal case
            nbr_data_received += len(content)
            total_data_received += len(content)
            duration = time.time() - time_begin
            if duration > 5:
                val_throughput = nbr_data_received / duration
                print( "INF: data throughput: %.1f/s (total: %.2fM)" % (val_throughput,total_data_received/(1000*1000)) )
                nbr_data_received = 0
                time_begin = time.time()

    print("%s: Closing connection" % getTimeStamp() )
    client.close()
    
"""
Stat:
Data received from 1 Esp32 (MisBKit 4) en burst: 
    - no wait: 1849-1954 bytes / sec.
    - no wait, check server connected between each bytes: 1739-1823 bytes / sec.
    - Teste non stop de 17h55 a 22h17 (4h20) sans coupure ni pertes de paquets. (avec les enfants qui font du wifi).
    
"""