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
    rSumVolHttp = 0
    rSumVolHttps = 0
    rSumVolArp = 0
    rSumVolUdp = 0
    rFrameVolTotal = 0
    rFrameVolHttp = 0
    rFrameVolHttps = 0
    rFrameVolArp = 0
    rFrameVolUdp = 0

    client.send_message("/global", [rSumVolTotal, rSumVolHttp, rSumVolHttps, rSumVolArp, rSumVolUdp,rFrameVolTotal, rFrameVolHttp, rFrameVolHttps, rFrameVolArp, rFrameVolUdp])
    time.sleep(0.01)

print("done")