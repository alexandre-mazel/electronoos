#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimpleHTTPServer
import SocketServer

import os
import time

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
    
    parameters = []    
    if( len( astrPathSplittedMark ) > 1 ):
        aRawParameters = astrPathSplittedMark[1].split("=")
        for i in range(0,len(aRawParameters),2):
            value = None
            if( len(aRawParameters) > i+1 ):
                value = aRawParameters[i+1]
            parameters.append([ aRawParameters[i], value ] )

    return [strFilename, strDirectoryName, parameters]
    
# analysePath - end
#~ retval = analysePath( "/playsound?file=../toto.wav" )    
#~ print( "analysePath: %s" % retval );
#~ exit()

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print( "INF: MyRequestHandler.get: dir: %s" % str(dir(self)) )
        print( "INF: MyRequestHandler.get: path: %s" % self.path )
        print( "INF: MyRequestHandler.get: client address: %s" % str(self.client_address) )
        print( "INF: MyRequestHandler.get: headers: %s" % str(self.headers) )
        print( "INF: MyRequestHandler.get: headers k: %s" % str(self.headers.keys()) )
        print( "INF: MyRequestHandler.get: headers ua: %s" % str(self.headers['user-agent']) )
        clientAddress = self.client_address
        strUserAgent = self.headers['user-agent']
        
        #~ self.wfile.write( "coucou test" )
        
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

        if( strPageName == "skipit" ):
            self.wfile.write( "<html>skipit_test" )
            timeBegin = time.time()
            import skipit
            #~ reload( skipit)
            actions = []
            if len(params)>0:
                actions = params[0]
            ret = skipit.run( clientAddress, strUserAgent, actions )
            self.wfile.write( ret )
            rDuration = time.time() - timeBegin
            self.wfile.write( "computation time: %5.2fs" % rDuration )
            return

        return; # prevent showing sources !
        
        #~ if self.path == '/':
            #~ self.path = '/simplehttpwebpage_content.html'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyRequestHandler
#~ print(dir(Handler))
server = SocketServer.TCPServer(('0.0.0.0', 80), Handler)

# print(dir(server))
print( "running..." )
try:
    server.serve_forever()
except:
    pass
server.server_close()