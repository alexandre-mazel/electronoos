import socket
import time
import datetime
import os
import threading

def getTimeStamp():
    """
    return (hour,min,second)
    """
    datetimeObject = datetime.datetime.now()
    return "%2dh%02dm%02d" % (datetimeObject.hour, datetimeObject.minute, datetimeObject.second)
    
    
def handle_client( conn, addr ):
    global total_data_received
    global total_time_begin
    
    print("INF: %s: %s: Client connected from port %s ..." % ( getTimeStamp(), str(addr[0]), str(addr[1]) ) )
    
    nPrevData = 99
    
    time_begin = time.time()
    nbr_data_received = 0;
    while True:
        flags = 0
        #~ if os.name != "nt":
            #~ flags |= socket.SOCK_NONBLOCK
        content = conn.recv(32,flags)

        if len(content) ==0:
           break
           
        #~ print(content)
        for data in content:
            #~ print( "0x%x" % data )
            if not ( data == nPrevData+1 or (data == 0 and nPrevData == 99) ):
                print("ERR: %s: %s: data corrupted (data: %d, nPrevData: %d)" % ( getTimeStamp(), str(addr[0]), data, nPrevData ) )
                conn.recv(4096) # flush all
                break
            nPrevData = data
        else:
            # normal case
            nbr_data_received += len(content)
            total_data_received += len(content)
            duration = time.time() - time_begin
            if duration > 5:
                val_throughput = nbr_data_received / duration
                duration_total = time.time()-total_time_begin
                val_throughput_total = total_data_received / duration_total
                # print data throughput
                print( "INF: %s: %s: %.1fB/s (total: %.1fB/s, %.2fMB, %.2fmin)" % ( getTimeStamp(), str(addr[0]), val_throughput, val_throughput_total, total_data_received/(1000*1000), duration_total/60 ) )
                nbr_data_received = 0
                time_begin = time.time()

    print("%s: %s: Closing connection" % (getTimeStamp(),str(addr[0]) ) )
    
    conn.close()
    
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

num_port = 8090
sock.bind(('0.0.0.0', num_port ))
sock.listen(10)
#~ sock.setdefaulttimeout(1.0)
sock.setblocking(0)

if os.name == "nt":
    print("INF: Cette version multithread non bloquant ne fonctionne pas sous windows")
    exit(-1)

print("INF: Serving socket on %s" % num_port )

total_data_received = 0
all_threads = []
total_time_begin = time.time()

try:
    while True:
        try:
            conn, addr = sock.accept()
        except OSError as err:
            import errno
            #~ print(str(errno.errorcode))
            if err.args[0] != errno.ETIMEDOUT and err.args[0] != errno.EAGAIN and (os.name == "nt" and err.args[0] != errno.WSAEWOULDBLOCK):
                print( "ERR: while accepting: oserror: %s" % str(err) )
            time.sleep(2)
            continue
        except Exception as err:
            print( "ERR: while accepting: error: %s" % str(err) )
            time.sleep(10)
            continue
        sock.settimeout(5) # kill if read received no information after 5 sec
        sock.setblocking(0)
        
        print("INF: %s: Client connected from %s..." % ( getTimeStamp(), str(addr) ) )
        
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()
        
        all_threads.append(t)
    
except KeyboardInterrupt:
    print("Stopped by Ctrl+C")
    
finally:
    if sock:
        sock.close()
    for t in all_threads:
        t.join()
        
"""
*** Stat monothread:
Data received from 1 Esp32 (MisBKit 4) => mstab7 en wifi en burst: 
    - no wait: 1849-1954 bytes / sec.
    - no wait, check server connected between each bytes: 1739-1823 bytes / sec.
    - Test non stop de 17h55 a 22h17 (4h20) sans coupure ni pertes de paquets (avec les enfants qui font du wifi).

Data received from 1 Esp32 (MisBKit 4) => rpi5 en eth en burst:   
    - no wait: 553-930 bytes / sec.
    
*** Stat multithread:
Data received from 2 Esp32 (MisBKit 4&5) => rpi5 en eth en burst:   
    - no wait: after 1045 bytes  / sec 100k
    - Test non stop 10h10 sans coupure ni pertes de paquets: total: 1231.5B/s, 45.10MB, 610.35min.
    - Un dans la chambre de Corto, un au fond du jardin: total: 1816.8B/s, 3.74MB, 34.27min.
    - no wait: 64kB/s par paquet de 100.
    - no wait: 500kB/s par paquet de 1000.
    - no wait: 700kB/s par paquet de 5000.



"""