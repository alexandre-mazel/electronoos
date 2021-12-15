import sys
import time
sys.path.append( "../versatile" )
from versatile import Versatile

class Logger:
"""File format:
Interval=    0.001 s
ExcelDateTime = 4.45104441204098883e+004 10/11/2021 10:35:20.034144
TimeFormat=
ChannelTitle =  Channel 3   Channel 4
Range=  2.00V   10.00V
0   -0.01    -0.068
0.001   -0.01   -0.068
"""

    def __init__(self):
        self.fout = open("/tmp/out.txt","wt")
        self.outputHeader()
        
    def getData(self):
        
        
    def __del__(self):
        self.fout.close()
        

    
    def outputHeader(self):
        self.fout.write()
        
    def log(strDataName, value):
        self.fout.write()
        self.fout.flush()


logger = Logger()


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
            logger.log(strDataName, value)
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