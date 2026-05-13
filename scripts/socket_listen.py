import socket
import time
 
s = socket.socket()         
 
s.bind(('0.0.0.0', 1032 ))
s.listen(0)                 
 
while True:
    client, addr = s.accept()
    client_ip,client_port = addr
 
    while True:
        content = client.recv(1024)
 
        if len(content) ==0:
           break
        
        print("INF: %.2f: %s: received: %s" % (time.time(),client_ip,content))

    print("INF: %.2f: %s: Closing connection" % (time.time(),client_ip))
    client.close()