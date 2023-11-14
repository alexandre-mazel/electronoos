from pythonosc.udp_client import SimpleUDPClient

"""
Simple script to encapsulate message the simplier possible.
Permits to have a main program calling it, but don't have to do anything special even if not connected
"""

class Sender:
    def __init__( self ):
        self.client = None
        
    def connect(strServerIP = "127.0.0.1", nPort = 8002)
        self.client = SimpleUDPClient(strServerIP, nPort)
        
    def sendMessage( strChannel, values ):
        if self.client != None: self.client.send_message(strChannel, values)
# class Sender - end