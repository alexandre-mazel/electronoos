from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

import time

USE_HTTPS = False

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        bExtraWait = 0
        #~ bExtraWait = 1
        
        print("%.3f: start %s get: " % (time.time(),self.path) + threading.currentThread().getName() + " " + str(threading.active_count()))
        self.send_response(200)
        self.end_headers()
        if bExtraWait: time.sleep(10)
        #self.wfile.write(b'Hello world\t' + threading.currentThread().getName().encode() + b'\t' + str(threading.active_count()).encode() + b'\n')
        f = open("./"+self.path,"rb")
        buf = f.read()
        f.close()
        self.wfile.write(buf)
        
        print("%.3f: fin write: " % time.time() + threading.currentThread().getName() + " " + str(threading.active_count()))
        if bExtraWait: time.sleep(10)
        print("%.3f: fin get: " % time.time() + threading.currentThread().getName() + " " + str(threading.active_count()))

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    print("test by typing: localhost:4444/www/test_big.htm")
    server = ThreadingSimpleServer(('0.0.0.0', 4444), Handler)
    if USE_HTTPS:
        import ssl
        server.socket = ssl.wrap_socket(server.socket, keyfile='./key.pem', certfile='./cert.pem', server_side=True)
    server.serve_forever()
    


if __name__ == '__main__':
    run()