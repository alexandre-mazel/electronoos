import time
from pythonosc.udp_client import SimpleUDPClient

# cf https://python-osc.readthedocs.io/en/latest/dispatcher.html#example

strServerIP = "127.0.0.1"
#~ strServerIP = "192.168.158.40"

client = SimpleUDPClient(strServerIP, 8002)

# Send message and receive exactly one message (blocking)
print("sending message...")
client.send_message("/filter1", 126)
time.sleep(2)
client.send_message("/filter1", 127)
time.sleep(2)
client.send_message("/pod", 127)
time.sleep(2)
client.send_message("/filter1", 200)
time.sleep(2)
client.send_message("/filter1", 666000)
time.sleep(2)
client.send_message("/filter1", 1.)
time.sleep(2)
client.send_message("/filter1", 666.)
time.sleep(2)
client.send_message("/filter1", [10,20])
time.sleep(2)
client.send_message("/filter1", [1., 2.,3])
print("done")