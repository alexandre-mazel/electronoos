"""
Socket: client device <=> server computer
Multi thread Version

NB: disconnection and reconnection of client is working.

Test1: the client send values from 0 to 100 regularly, the server check if all datas arrived.
(it can be packet of any size: 1 bytes, 100 bytes, 5000 bytes...)


(c) A.Mazel for EnsadLab 2024-2025
"""

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
    
def smartFormatSize( size ):
    if size < 10:
        return "%.3f" % size
    if size < 1000:
        return "%.1f" % size
    if size < 1000*1000:
        return "%.1fk" % (size/1000)
    if size < 1000*1000*1000:
        return "%.1fM" % (size/(1000*1000))
        
    return "%.1fG" % (size/(1000*1000*1000))
    
def receiveData100( conn, addr ):
    global total_data_received
    global total_time_begin
    
    nbr_data_received = 0;
    nPrevData = 99
    
    time_begin = time.time()
    
    while True:
        flags = 0
        #~ if os.name != "nt":
            #~ flags |= socket.SOCK_NONBLOCK
        try:
            content = conn.recv(32,flags)
        except BaseException as err:
            if (os.name == "nt" and err.args[0] != errno.WSAEWOULDBLOCK):
                print( "ERR: while receving: error: %s" % str(err) )
            continue

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
                print( "INF: %s: %s: %sB/s (total: %sB/s, %sB, %.2fmin)" % ( getTimeStamp(), str(addr[0]), smartFormatSize(val_throughput), smartFormatSize(val_throughput_total), smartFormatSize(total_data_received), duration_total/60 ) )
                nbr_data_received = 0
                time_begin = time.time()
                
def sendData100( conn, addr ):
    print("INF: %s: %s: Sending data100s to client" % ( getTimeStamp(), str(addr[0]) ) )
    buf = []
    for i in range( 100 ):
        buf.append( i%100 ) # beurk
    buf = bytes( buf )
        
    for i in range(1000000):
        conn.send( buf )
        time.sleep( 0.00001 )
        if os.name == "nt" and 0:
              # depuis windows si trop rapide => BlockingIOError: [WinError 10035] Une operation non bloquante sur un socket n'a pas pu etre achevee immediatement.
              time.sleep( 0.0001 )
            
    print("INF: %s: %s: Sending data100s to client - done" % ( getTimeStamp(), str(addr[0]) ) )
    
def handle_client( conn, addr ):
    
    print("INF: %s: %s: Client connected from port %s ..." % ( getTimeStamp(), str(addr[0]), str(addr[1]) ) )
    
    #~ receiveData100( conn, addr )
    sendData100( conn, addr )

    print("%s: %s: Closing connection" % (getTimeStamp(),str(addr[0]) ) )
    
    conn.close()
    
if __name__ == "__main__":
        
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    num_port = 8090
    sock.bind(('0.0.0.0', num_port ))
    sock.listen(10)
    #~ sock.setdefaulttimeout(1.0)
    sock.setblocking(0)

    # Yes it works now under windows!
    # even when client disconnect and reconnect
    #~ if os.name == "nt":
        #~ print("INF: Cette version multithread non bloquant ne fonctionne pas sous windows")
        #~ exit(-1)

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
            print( "INF: nbr created thread(s): %d" % len(all_threads))
        
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
    - no wait: 700kB/s send par paquet de 5000 (avec les enfants qui font du wifi).
    
Data received from 1 Esp32 (MisBKit 4) => rpi5 en eth en burst:   
    - no wait: 553-930 bytes / sec.
    
*** Stat multithread:
Data received from 2 Esp32 (MisBKit 4&5) => rpi5 en eth en burst:
    - no wait: after 1045 bytes  / sec 100k
    - Test non stop 10h10 sans coupure ni pertes de paquets: total: 1231.5B/s, 45.10MB, 610.35min.
    - Un dans la chambre de Corto, un au fond du jardin: total: 1816.8B/s, 3.74MB, 34.27min.
    - no wait: 64kB/s send par paquet de 100.
    - no wait: 500kB/s send paquet de 1000.
    - no wait: 700kB/s send paquet de 5000.
    
Data received mstab7 => MisBKit 5:
    -      5 - 6 kB/s avec un read par paquet de 10.
    - 6.7 - 8.4 kB/s avec un read par paquet de 100. - vieux code plus precis sur le debit
    -            6 kB/s avec un read par paquet de 1000.
    -            6 kB/s avec un read par paquet de 2000.
    -            6 kB/s avec un read par paquet de 5000 - plante a l'envoi (car lit pas assez vite?)
    
Data received rpi5 eth => MisBKit 5:
    - 379 - 382 kB/s avec un read par paquet de 10.
    - 714 - 754 kB/s avec un read par paquet de 100.
    - 595 - 780 kB/s avec un read par paquet de 1000.
    - 646 - 772 kB/s avec un read par paquet de 2000.
    - 121 - 522 kB/s avec un read par paquet de 5000. (oui etonnamment, c'est plus lent)



"""