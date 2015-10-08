#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def __init__( self ):
        print( "INF: MyHTTPRequestHandler: init" )
    
    #handle GET command
    def do_GET(self):
        print( "INF: MyHTTPRequestHandler.do_GET: path: %s" % str(self.path) )

        rootdir = './' #file location
        try:
            if self.path.endswith('.html'):
                f = open(rootdir + self.path) #open requested file

                #send code 200 response
                self.send_response(200)

                #send header first
                self.send_header('Content-type','text-html')
                self.end_headers()

                #send file content to client
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404, 'file not found')
          
# class MyHTTPRequestHandler - end
          
def run():
  print('http server is starting...')
 
  #ip and port of server
  #by default http server port is 80
  server_address = ('127.0.0.1', 8000)
  httpd = HTTPServer(server_address, MyHTTPRequestHandler)
  #~ httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
  print('http server is running...')
  httpd.serve_forever()
  
if __name__ == '__main__':
  run()