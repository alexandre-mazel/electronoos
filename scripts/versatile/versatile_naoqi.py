# -*- coding: utf-8 -*-
###########################################################
# Send data from a simple device (raspberry, gpu, watch) to a robot thru ALMemory
# syntaxe:
#       python scriptname robot_ip dataname [value] or python scriptname start_server
#       eg: python scriptname 192.168.0.4 HeadTouched  (or  ALTextToSpeech/CurrentSentence)
#           will return "1"
#       eg: python scriptname 192.168.0.4 step 5
#           will return set the data step to "5"
# Aldebaran Robotics (c) 2008 All Rights Reserved
###########################################################

from versatile import Versatile

import naoqi

import numpy
import sys
import time

class RobotCamera:
    def __init__( self ):
        self.nCurrentResolution = -1
        
    def __del__( self ):
        self.disconnectFromCamera()
        
    def getCurrentResolution( self ):
        return self.nCurrentResolution

    def connectToCamera( self, nCameraNum = 0, nResolution = 2, nColorspace = 11, nFps = 20 ):
        print( "INF: connecting to camera, nCameraNum = %s, nResolution = %s, nColorspace = %s, nFps = %s" % (nCameraNum, nResolution, nColorspace, nFps) )
        try:
            self.avd = naoqi.ALProxy( "ALVideoDevice", "localhost", 9559 )
            strMyClientName = "VersatileRobotCamera_" + str(time.time()) # generate a different name each time
            self.strMyClientName = self.avd.subscribeCamera( strMyClientName, nCameraNum, nResolution, nColorspace, nFps );
            self.nCurrentResolution = nResolution
        except BaseException, err:
            print( "ERR: connectToCamera: catching error: %s!" % err )

    def disconnectFromCamera( self ):
        try:
            self.avd.unsubscribe( self.strMyClientName )
        except BaseException, err:
            print( "ERR: disconnectFromCamera: catching error: %s!" % err )

    def getImageFromCamera( self ):
        """
        return the image from camera or None on error
        """
        try:
            dataImage = self.avd.getImageRemote( self.strMyClientName )

            if( dataImage != None ):
                image = (numpy.reshape(numpy.frombuffer(dataImage[6], dtype='%iuint8' % dataImage[2]), (dataImage[1], dataImage[0], dataImage[2])))
                return image

        except BaseException, err:
            print( "ERR: getImageFromCamera: catching error: %s!" % err )
        return None

# class RobotCamera - end

class VersatileALMemory(Versatile):
    """
    cf Versatile. Actually only the server part is changing
    """
    def __init__(self):
        Versatile.__init__(self)
        self.robotCamera = None
        
    def getNewImage( self, nNumCamera, nResolution, nFormat ):
        """
        return (time stamp, image)
        please inherits this method in your own program
        """
        #~ print( "DBG: VersatileALMemory.getNewImage: entering..." )
        # TODO: here's a bug when many client at same time asking for various settings
        if self.robotCamera == None or nResolution != self.robotCamera.getCurrentResolution():
            self.robotCamera = RobotCamera()
            # convert from versatile color space to naoqi color space
            nNaoqiFormat = 0
            if nFormat == Versatile.VersatileImage.Format.JPG or nFormat == Versatile.VersatileImage.Format.PNG:
                nNaoqiFormat = 13
            self.robotCamera.connectToCamera( nNumCamera, nResolution, nNaoqiFormat )
        img = self.robotCamera.getImageFromCamera()
        return (time.time(),img)
        
    def handleCommand( self, command, command_parameters, client = None ):
        """
        please inherits this method in your own program
        """

        if command == Versatile.nCommandType_Get:
            strDataName = command_parameters[0]
            try: 
                valueFromALMemory = self.mem.getData(strDataName)
            except:
                #print( "DBG: data '%s' isn't in the Memory" % (strDataName) )
                valueFromALMemory = None # non existing value
            return valueFromALMemory
            
        if command == Versatile.nCommandType_Set:
            strDataName = command_parameters[0]
            value = command_parameters[1]
            self.mem.raiseMicroEvent(strDataName,value)
            return 1
        
        #~ if command == Versatile.nCommandType_SubscribeCamera:  
            # done in the inherits class, just specialize the getNewImage method
        
        # other command keep standard behavior
        return Versatile.handleCommand( self, command, command_parameters, client )
            
        
    def runServer( self, nNaoqiPort = 9559 ):
        """
        run an infinite server
        """
        print( "INF: versatile_naoqi: starting server..." )
        self.mem = naoqi.ALProxy( "ALMemory", "localhost", nNaoqiPort )
        Versatile.runServer(self)
        
# class VersatileALMemory - end
    
    
def run_server(nNaoqiPort):
    print( "INF: versatile: starting server..." )
    v = VersatileALMemory()
    v.runServer(nNaoqiPort)
    
if( __name__ == "__main__" ):
    
    def print_syntax():
        print( "syntax: scriptname robot_ip variable_name [value]" )
        print( "Exemple: scriptname robot_ip DCM/Time" )        
        print( "or:" )
        print( "syntax: to start a server: scriptname start_server [naoqi_port]" )
        exit( 0 )

    if len(sys.argv) < 2:
        print_syntax()
    strIP = sys.argv[1]
    if strIP == "start_server":
        nNaoqiPort = 9559
        if len(sys.argv) > 2:
            nNaoqiPort = int(sys.argv[2])    
        run_server(nNaoqiPort)
        exit(1)    
        
    if len(sys.argv) < 3:
        print_syntax()
    
    
    strDataName = sys.argv[2]
    strValue = None
    if len(sys.argv)>3:
        strValue = sys.argv[3]
        
    retVal = connectAndSend( strIP, strDataName, strValue )
    print( "return:\n%s" % str(retVal) )