from pythonosc.udp_client import SimpleUDPClient

"""
Simple script to encapsulate message the simplier possible.
Permits to have a main program calling it, but don't have to do anything special even if not connected
"""

class Sender:
    def __init__( self ):
        self.client = None
        
    def connect( self, strServerIP = "127.0.0.1", nPort = 8002 ):
        self.client = SimpleUDPClient(strServerIP, nPort)
        
    def sendMessage( self, strChannel, values ):
        #~ print("DBG: Sender.sendMessage: self.client: %s" % str(self.client))
        if self.client != None: 
            print("DBG: Sender.sendMessage: sending: %s: %s" % (strChannel, values))
            self.client.send_message(strChannel, values)
# class Sender - end