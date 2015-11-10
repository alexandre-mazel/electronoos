#!/usr/bin/env python
# upload me:
# scp -pw raspberry C:\work\Dev\git\electronoos\raspberry\system\sound_server\s*.py pi@10.0.161.58:/home/pi/sound_server/
# 
import SimpleHTTPServer
import SocketServer

import datetime
import os
import time

def analysePath( strPath ):
    """
    analyse a html request path
    - strPath: a path and command, eg: "/playsound?file=../toto.wav"
    return an array: [filename, directory_name, parameters,raw_parameters]
    with:
    - filename: the name of the file, eg: "playsound"
    - directory_name: the requested location, eg: "/"
    - parameters: a dict of parameters pair, eg: [{"file" => "../toto.wav}]
    - raw_parameters: the parameters as received: "file=../toto.wav"
    """

    astrPathSplittedMark = strPath.split( "?")
    strPathWithoutParameters = astrPathSplittedMark[0]
    strDirectoryName = os.path.dirname( os.path.abspath(strPathWithoutParameters) )
    #~ print( "strDirectoryName: %s" % strDirectoryName )

    strFilename = os.path.basename( strPathWithoutParameters )
    print( "strFilename: %s" % strFilename )

    parameters = {}
    raw_parameters = ""

    if( len( astrPathSplittedMark ) > 1 ):
        raw_parameters = astrPathSplittedMark[1]
        aRawParametersPair = astrPathSplittedMark[1].split("&")
        print( "aRawParametersPair: %s" % aRawParametersPair )
        for aParameterPair in aRawParametersPair:
            aRawParameters = aParameterPair.split("=")
            print( "aRawParameters: %s" % aRawParameters )
            for i in range(0,len(aRawParameters),2):
                parameters[aRawParameters[i]] = aRawParameters[i+1]

    return [strFilename, strDirectoryName, parameters, raw_parameters]
    
# analysePath - end
#~ retval = analysePath( "/playsound?file=../toto.wav" )    
#~ print( "analysePath: %s" % retval );
#~ exit()


def getFilenameFromTime(timestamp=None):
  """
  get a string usable as a filename relative to the current datetime stamp.
  eg: "2012_12_18-11h44m49s049ms"
  
  timestamp : time.time()
  """
  if timestamp is None:
      datetimeObject = datetime.datetime.now()
  elif isinstance(timestamp, datetime.datetime):
      datetimeObject = timestamp
  else:
      datetimeObject = datetime.datetime.fromtimestamp(timestamp)
  strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
  strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds
  return strTimeStamp;
# getFilenameFromTime - end
#~ print( getFilenameFromTime() );

def executeAndGrabOutput( strCommand, bQuiet = False ):
  "execute a command in system shell and return grabbed output"
  "WARNING: it's a 'not efficient' function!"
  strTimeStamp = getFilenameFromTime();
  strOutputFilename = "/tmp/" + "grab_output_" + strTimeStamp+ ".tmp"; # generate a different file each call for multithreading capabilities
  strTotalCommand = strCommand + " >" + strOutputFilename;
  os.system( strTotalCommand );
  file = open( strOutputFilename )
  strBufferRead = file.read()
  file.close()
  try:
    os.unlink( strOutputFilename );
  except:
    pass
  if( not bQuiet ):
    debug.debug( "executeAndGrabOutput: '%s'" % strBufferRead );
  return strBufferRead;
# executeAndGrabOutput - end

def getMasterVolume():
    """
    get sound system volume (in %)"
    Return a pair [volR,volL]
    """
    
    strOutput = executeAndGrabOutput( "amixer sget Speaker | grep 'Front Right: Playback' | cut -d' ' -f6", True );
    nValR = int( strOutput );
    strOutput = executeAndGrabOutput( "amixer sget Speaker | grep 'Front Left: Playback' | cut -d' ' -f6", True );
    nValL = int( strOutput );
    return (nValR,nValL);
# getMasterVolume - end

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def __init__( self, request, client_address, server ):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__( self, request, client_address, server )
        pass
        
    def do_GET(self):
        
        print( "INF: MyRequestHandler.get: path: %s" % self.path )
        
        # parse command
        retval = analysePath(self.path)
        print( "analysePath return: %s" % retval )
        strPageName, dirName, params, raw_param = retval
        
        # playsound?file=toto.wav
        if( strPageName == "playsound" ):
            print( "INF: MyRequestHandler.get: playsound: params: %s" % params )
            strFilename = params["file"]
            try:
                nVolume = int(params["volume"])
            except:
                nVolume = 100

            strOutput = "Playing file: '%s'...<br> with volume %d%%\n" % (strFilename, nVolume)            
            print( "INF: " + strOutput )
            self.wfile.write( strOutput )
            self.wfile.flush()                
            
            if( 1 ):
                # set volume
                nCoefR = nCoefL = nVolume
                nCoefR = nCoefR * 151 / 100;
                nCoefL = nCoefL * 151 / 100;
                #print( "DBG: vol coef: %s" % str(nCoefL) )
                aCurrentVolume = getMasterVolume()
                if( aCurrentVolume != (nCoefR,nCoefL) ):
                    print( "DBG: really changing volume: %s != %s" % (aCurrentVolume, (nCoefR,nCoefL)) )
                    retcall = os.system( "amixer -q sset Speaker %d,%d" % ( nCoefL, nCoefR ) );                
                    time.sleep( 0.6 ) # the sound card takes a bit before changing the volume
                
            retcall = os.system( "aplay %s" % strFilename )
            print( "retcall : %s" % retcall )
            self.wfile.write("Return: Success: %s" % (retcall==0))
            return;

        
        #~ if self.path == '/':
            #~ self.path = '/simplehttpwebpage_content.html'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyRequestHandler
nNumPort = 8000
server = SocketServer.TCPServer(('0.0.0.0', nNumPort), Handler)

print( "Running sound server on port %d ..." % nNumPort )

try:
    #~ print( dir(server) )
    server.serve_forever()
except:
    pass # catch all info, so we could continue the program
print( "Cleaning...\n" )
server.server_close()