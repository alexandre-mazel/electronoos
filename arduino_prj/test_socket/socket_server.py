import socket
import time

sock = socket.socket()         

num_port = 8090
sock.bind(('0.0.0.0', num_port ))
sock.listen(0)

print("INF: Serving socket on %s" % num_port )

total_data_received = 0

while True:
    client, addr = sock.accept()
    
    print("INF: Client connected from %s..." % str(addr) )
    
    nPrevData = 99
    
    time_begin = time.time()
    nbr_data_received = 0;
    while True:
        content = client.recv(256)

        if len(content) ==0:
           break
           
        #~ print(content)
        for data in content:
            #~ print( "0x%x" % data )
            if not ( data == nPrevData+1 or (data == 0 and nPrevData == 99) ):
                print("ERR: data xcorrupted (data: %d, nPrevData: %d)" % (data,nPrevData) )
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

    print("Closing connection")
    client.close()
    
"""
Stat:
    - Data received from esp32 burst: 1849-1954 bytes / sec.
"""