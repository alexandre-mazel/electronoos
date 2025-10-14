import socket
import time
import sys

def send_values(host="127.0.0.1", port=9000, values=(421)):
    """Send a list of values to the server as text messages."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if 0:
            for v in values:
                msg = str(v).encode()
                s.sendall(msg + b"\n")
                print(f"Sent: {v}")
                time.sleep(0.5)  # small pause between sends
        else:
            msg = str(values).encode()
            s.sendall(msg + b"\n")
            print(f"Sent: {values}")
            
host = "127.0.0.1"
host = "192.168.0.60"
host = "192.168.9.110"
            
def set_color( chan, val = 255, dur = 1.0 ):
    for i in range(8):
        send_values(host=host,values=(chan+i, val, dur))
        
def set_indigo( chan, val = 255, dur = 1.0 ):
    for i in range(6):
        send_values(host=host,values=(chan+i, 0, dur))
    send_values(host=host,values=(chan+6, val, dur))
    send_values(host=host,values=(chan+7, val, dur))
    

if __name__ == "__main__":
    chan = 220
    val = 255
    if len(sys.argv)>1:
        chan = int(sys.argv[1])
    # send a channel, a value and a time
    #~ send_values(host=host,values=(181, 255, 1.0))
    #~ for i in range(1, 33):
        #~ set_color( i*10, 0 )
    set_color( 220, 255 )
    #~ set_indigo( 80, 255 )
    #~ set_indigo( 90, 255 )