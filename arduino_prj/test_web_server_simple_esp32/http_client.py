import http.client
import time

import sys
sys.path.append("../test_socket")
from socket_server import getTimeStamp, smartFormatSize


conn = http.client.HTTPConnection("192.168.0.9")

if 0:
    conn.request("GET", "/")
    r1 = conn.getresponse()
    print(r1.status, r1.reason)

    data1 = r1.read()  # This will return entire content.

received_size = 0
time_begin = time.time()
nbr_exchange = 0
nbr_received = 0
nbr_sent = 0
        
while 1:
    # The following example demonstrates reading data in chunks.
    msg_to_send = "/motor?234532"
    nbr_sent += len( msg_to_send )
    conn.request("GET", msg_to_send)
    r1 = conn.getresponse()
    while chunk := r1.read(30):
        #~ print(repr(chunk))
        nbr_received += len(chunk)
    time.sleep( 0.0001 )
    
    nbr_exchange += 1
    duration = time.time() - time_begin
    if duration > 5:
        received = nbr_received / duration
        sent = nbr_sent / duration
        print( "%s: nbr_exchange: %.1f (%d), Sent: %sB, Received: %sB, Total: %sB" % ( getTimeStamp(), nbr_exchange/duration, nbr_exchange, smartFormatSize(sent), smartFormatSize(received), smartFormatSize(sent+received) ) )
        time_begin = time.time()
        nbr_exchange = 0
        nbr_received = 0
        nbr_sent = 0


if 0:
    # Example of an invalid request
    conn = http.client.HTTPSConnection("docs.python.org")
    conn.request("GET", "/parrot.spam")
    r2 = conn.getresponse()
    print(r2.status, r2.reason)

    data2 = r2.read()
    conn.close()