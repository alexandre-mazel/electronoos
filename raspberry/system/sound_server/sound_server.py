#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer

import os

def analysePath( strPath ):
    """
    analyse a html request path 
    - strPath: a path and command, eg: "/playsound?file=../toto.wav"
    return an array: [filename, directory_name, parameters]
    with:
    - filename: the name of the file, eg: "playsound"
    - directory_name: the requested location, eg: "/"
    - parameters: a list of parameters pair, eg: [["file", "../toto.wav]]
    """
    
    astrPathSplittedMark = strPath.split( "?")
    strPathWithoutParameters = astrPathSplittedMark[0]
    strDirectoryName = os.path.dirname( os.path.abspath(strPathWithoutParameters) )
    #~ print( "strDirectoryName: %s" % strDirectoryName )
    
    strFilename = os.path.basename( strPathWithoutParameters )
    print( "strFilename: %s" % strFilename )
    
    if( len( astrPathSplittedMark ) > 1 ):
        parameters = []
        aRawParameters = astrPathSplittedMark[1].split("=")
        for i in range(0,len(aRawParameters),2):
            parameters.append([ aRawParameters[i], aRawParameters[i+1] ] )

    return [strFilename, strDirectoryName, parameters]
    
# analysePath - end
#~ retval = analysePath( "/playsound?file=../toto.wav" )    
#~ print( "analysePath: %s" % retval );
#~ exit()

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print( "INF: MyRequestHandler.get: path: %s" % self.path )
        
        # parse command
        retval = analysePath(self.path)
        print( "analysePath return: %s" % retval )
        strPageName, dirName, params = retval
        
        # playsound?file=toto.wav
        if( strPageName == "playsound" ):
            print( "INF: MyRequestHandler.get: playsound: params: %s" % params )
            for param in params:
                name, value = param
                if( name == "file" ):
                    print( "playing file: %s" % value )
                    self.wfile.write("Playing file: '%s'...<br>\n" % value)
                    self.wfile.flush()
                    retcall = os.system( "aplay %s" % value )
                    print( "retcall : %s" % retcall )
                    self.wfile.write("Return: Success: %s" % (retcall==0))
            return;

        
        #~ if self.path == '/':
            #~ self.path = '/simplehttpwebpage_content.html'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyRequestHandler
#~ print(dir(Handler))
server = SocketServer.TCPServer(('0.0.0.0', 8000), Handler)

print( "running..." )
server.serve_forever()