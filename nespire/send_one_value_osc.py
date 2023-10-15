# pip3 install python-osc
from pythonosc.udp_client import SimpleUDPClient

ip = "192.168.4.2"
port = 8003

ip = "192.168.4.3"
port = 8002

client = SimpleUDPClient(ip, port)  # Create client

client.send_message("/oscin1", 1)   # Send float message
#~ client.send_message("/oscin1", 0.9)   # Send float message
#~ client.send_message("/chan1", 0.5)   # Send float message
#~ client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string