import socket

s = socket.socket()         

num_port = 8090
s.bind(('0.0.0.0', num_port ))
s.listen(0)  

print("INF: Serving socket on %s" % num_port )

while True:
    client, addr = s.accept()
    nPrevData = 
    time_begin = time.time()
    while True:
        content = client.recv(32)

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
                
                

    print("Closing connection")
    client.close()