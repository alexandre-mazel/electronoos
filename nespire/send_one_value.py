import socket

def sendData(ip, port, msg):
    print("DBG: sendData '%s' to %s:%s" % (msg,ip,port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # DGRAM => UDP
    data = str.encode(msg)
    sock.sendto(data,(ip,port))
    
#~ sendData("192.168.4.3", 8002, "coucou")
sendData("192.168.4.2", 8003, "#bundle00000000_/oscin1,i")