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

client.send_message("/global_labels", ["rSumVolTotal", "rSumVolHttp", "rSumVolHttps", "rSumVolArp", "rSumVolUdp","rFrameVolTotal", "rFrameVolHttp", "rFrameVolHttps", "rFrameVolArp", "rFrameVolUdp","0","1","-1","1000","-1000"])
time.sleep(0.1)

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
    rSlowSin = math.sin(time.time()/10)
    rNegSin = math.sin(time.time()/2)-100

    client.send_message("/global", [rSumVolTotal, rSumVolHttp, rSumVolHttps, rSumVolArp, rSumVolUdp,rFrameVolTotal, rFrameVolHttp, rFrameVolHttps, rFrameVolArp, rFrameVolUdp,rSlowSin,rNegSin,0,1,-1,1000,-1000])
    #~ client.send_message("/global", [rFrameVolArp])
    time.sleep(0.01)
    #~ break

print("done")