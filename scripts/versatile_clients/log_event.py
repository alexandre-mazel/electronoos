import cv2
import sys
import time
sys.path.append( "../versatile" )
from versatile import Versatile

class VersatileLogEvents(Versatile):
    """
    cf Versatile. Actually only the server part is changing
    """
    def __init__(self):
        Versatile.__init__(self)
        
    def handleCommand( self, command, command_parameters, client = None ):
        """
        please inherits this method in your own program
        """

        if command == Versatile.nCommandType_Set:
            strDataName = command_parameters[0]
            value = command_parameters[1]
            print("INF: VersatileLogEvents.handleCommand: received data: %s, value: %s" % (strDataName, value) )
            # log it !
            return 1
        
        # other command keep standard behavior
        return Versatile.handleCommand( self, command, command_parameters, client )
            
        
    def runServer( self ):
        """
        run an infinite server
        """
        print( "INF: versatile_log_events: starting server..." )
        Versatile.runServer(self)
        
# class VersatileLogEvents - end

def logEvents():
    v = VersatileLogEvents()
    v.runServer()
# showBroadcast - end

#~ if len( sys.argv ) < 3:
    #~ print( "syntax: scriptname ip broadcaster_id" )

logEvents()