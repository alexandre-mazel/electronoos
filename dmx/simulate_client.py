import socket
import time

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

if __name__ == "__main__":
    # send a channel, a value and a time
    host = "127.0.0.1"
    host = "192.168.0.60"
    send_values(host=host,values=(200, 33, 1.0))