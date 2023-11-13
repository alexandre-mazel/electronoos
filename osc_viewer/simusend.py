import math
import time
from pythonosc.udp_client import SimpleUDPClient

# cf https://python-osc.readthedocs.io/en/latest/dispatcher.html#example

strServerIP = "127.0.0.1"
#~ strServerIP = "192.168.158.40"

nPort = 8002

client = SimpleUDPClient(strServerIP, nPort)

# Send message and receive exactly one message (blocking)
print("sending message to %s:%s..." % (strServerIP,nPort))
while 1:
    rSumVolTotal = time.time()%10.
    rSumVolHttp = math.sin(time.time()*10)+2
    rSumVolHttps = math.sin(time.time()*10)+1
    rSumVolArp = math.sin(time.time()*10)-1
    rSumVolUdp = math.sin(time.time()*10)
    rFrameVolTotal = math.sin(time.time()*10)*10
    rFrameVolHttp = math.sin(time.time()*10)*0.1
    rFrameVolHttps = int(time.time()%11)-5
    rFrameVolArp = int(time.time()%10)
    rFrameVolUdp = math.sin(time.time())

    client.send_message("/global", [rSumVolTotal, rSumVolHttp, rSumVolHttps, rSumVolArp, rSumVolUdp,rFrameVolTotal, rFrameVolHttp, rFrameVolHttps, rFrameVolArp, rFrameVolUdp])
    time.sleep(0.01)

print("done")