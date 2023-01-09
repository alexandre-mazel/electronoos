from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import ssl

import gzip
import os
import importlib
import sys
import time

class MyServer:
    def __init__(self):
        self.strName = "AlexServ"
        self.strVersion = "0.6"
        
        self.loadedFiles = {} # filename => timstamp read, buf

        self.counter = 0
        
        self.bDev = 1
        self.bDev = 0
        
myServer = MyServer()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self,request, client_address, server):
        self.server_version = myServer.strName
        self.sys_version = myServer.strVersion
        super().__init__(request, client_address, server)
        
    def end_headers(self):
        self.send_my_headers()
        super().end_headers()

    def send_my_headers(self):
        #~ print("DBG: send_my_headers: path: %s" % self.path)
        if ".png" in self.path or ".woff" in self.path or ".jpg" in self.path:
            #~ print("DBG: caching 100 min")
            self.send_header("Cache-Control", "max-age=6000")
            
        if ".html" in self.path:
            self.send_header("Content-Type", "text/html; charset=cp1252")
            
        if self.bOutputIsGzipped:
            self.send_header("Content-Encoding", "gzip")
            
        #~ cookie = SimpleCookie()
        #~ cookie['a_cookie'] = "Cookie_Value"
        #~ cookie['b_cookie'] = "Cookie_Value2"

        #~ for morsel in cookie.values():
            #~ self.send_header("Set-Cookie", morsel.OutputString())

    def sendCookie(self,name,value,expireInSec=0):
        print("DBG: sendCookie: Send cookies: %s: %s" % (name,value) )
        s = "%s=%s;Path=/" % (name,value)
        if expireInSec != 0:
            s += "; Max-Age=%d" % expireInSec
        self.send_header("Set-Cookie", s)
        
    def getCookie(self,name, defaultValue = ""):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        print("DBG: getCookie: cookies: %s" % cookies)
        try:
            value = cookies[name]
        except KeyError as err:
            value = defaultValue
            
        print("DBG: getCookie: %s => %s" % (name,value) )
        return value
        
    def fillReq(self,req):
        """
        store classical information in req for compat with mod_python
        """
        req.hostname = ""
        req.status = ""
        req.server = ""
        req.filename = ""
        req.construct_url = ""
        req.document_root = ""
        req.path_info = ""
        req.uri = ""
        req.get_remote_host = lambda  : ""

    def do_GET(self):
        """
        page https://192.168.0.14:4443/vitrine/about.htm
        test dans firefox, debugger reseau.
        Si on fait shift-F5 ca recharge meme si c'etait dans le cache. (de meme si l'option "desactiver le cache" dans le debugger est mise)
        takes about:
        - mstab7: 650ms
        - on rpi4: 1.30s
        - on rpi4: en utilisant global_loadedFiles, ca ne gagne pas grand chose 1.10?
        - ce qui gagne vraiment, c'est de renvoyer un cache control sur les images et fontes woff => 420ms
        - official website: 5.51s (avec cache 465ms)
        
        # un truc different: apache retourne les donnees en gzip, p.ex pour stylefont.css, la requete fait 680o au lieu de 2,60ko (le content-len est 325)
        # alors que ce server retourne un fichier de 2.68k
        # firefox avait envoye dans l'entete de requete un accept-encoding gzip, deflat, br
        # done, now stylefont.css, est une requete de 427o (le gzip est sauve dans le cache de fichiers loadedFile, c'est top!)
        

        """
        bVerbose = 1
        bVerbose = 0
        
        #~ cookies = SimpleCookie(self.headers.get('Cookie'))
        #~ print("cookies: %s" % cookies )
        
        self.bOutputIsGzipped = 0
        self.bOutputIsGzipped = 1
        
        if bVerbose: print("INF: do_GET: entering...")
        if bVerbose: print("DBG: do_GET: self.path: %s" % self.path)
        if self.path == '/':
            self.path = "index.html"
        if self.path == '/vitrine/':
            self.path = "/vitrine/index.html"
            
        if self.path[0] == '/':
            self.path = self.path[1:]
            
        if "/vitrine/" == self.path[:9]:
            self.path = "." + self.path
            
        if "/www/" == self.path[:5]:
            self.path = "." + self.path
            
        if bVerbose: print("DBG: do_GET: self.path(2): %s" % self.path)
        
        idx_interro = self.path.find('?')
        params = ""
        if idx_interro != -1:
            params = self.path[idx_interro+1:]
            self.path = self.path[:idx_interro]
            
        if bVerbose: print("DBG: do_GET: self.path(3): %s" % self.path)
        
        
        self.send_response(200)
        
        #~ self.wfile.write(b'Hello, world!')
        if ".py" == self.path[-3:]:
            print( "DBG: do_GET: python script!" )
            req = type('', (), {})()
            self.fillReq(req)
            req.args = params
            pathname, filename = os.path.split(self.path)
            filename_without_ext = filename.replace(".py","")

            print( "DBG: do_GET: self.path: %s" % self.path )
            print( "DBG: do_GET: req.args: %s" % req.args )
            print( "DBG: do_GET: filename: %s" % filename )
            #~ mod = importlib.import_module(self.path,filename)
            sys.path.append(pathname)
            mod = importlib.import_module(filename_without_ext)
            
            #~ ret = mod.index(req,myServer)
            req.server = myServer
            req.handler = self
            
            timeBegin = time.time()
            
            ret = mod.index(req)
            
            if myServer.bDev:
                bar = "#"*40
                print(bar)
                print("# python answer:")
                print(ret)
                print(bar)
                
            print( "DBG: do_GET: python executed in %.2fs" % (time.time()-timeBegin) )
                
            binret = ret.encode('ascii')
            if self.bOutputIsGzipped:
                binret = gzip.compress(binret)
                
            self.end_headers()
            self.wfile.write(binret)
            return
            
        
        bMustLoad = False
        try:
            
            #~ buf = self.loadedFiles[self.path]
            filestamp,buf = myServer.loadedFiles[self.path]
            if myServer.bDev:
                # check file isn't changed on disk
                if filestamp < os.path.getmtime(self.path):
                    bMustLoad = True
            
        except KeyError:
            bMustLoad = True
            
        if bMustLoad:
            print("DBG: real loading of %s" % self.path)
            try:
                f = open(self.path,"rb")
                buf = f.read()
                f.close()
                if self.bOutputIsGzipped and not ".gz" in self.path:
                    buf = gzip.compress(buf)
                myServer.loadedFiles[self.path] = time.time(),buf
            except FileNotFoundError:
                print("DBG: file not found: '%s" % self.path)
                return
        
        self.end_headers()                
        self.wfile.write(buf)
        
        
        # untested:
        # cf https://blog.anvileight.com/posts/simple-python-http-server/
    #~ def do_POST(self):
        #~ content_length = int(self.headers['Content-Length'])
        #~ body = self.rfile.read(content_length)
        #~ self.send_response(200)
        #~ self.end_headers()
        #~ response = BytesIO()
        #~ response.write(b'This is POST request. ')
        #~ response.write(b'Received: ')
        #~ response.write(body)
        #~ self.wfile.write(response.getvalue())

#~ The request body can be accessed via self.rfile. It is a BufferedReader so read([size]) method should be executed in order to get the contents. Note, that size should be explicitly passed to the function, otherwise the request will hang and never end.

#~ This is why obtaining content_length is necessary. It could be retrieved via self.headers and converted into an integer. An example above just prints back whatever he receives, like follows:

#~ http http://127.0.0.1:8000 key=value
#~ HTTP/1.0 200 OK
#~ Date: Sun, 25 Feb 2018 17:46:06 GMT
#~ Server: BaseHTTP/0.6 Python/3.6.1

#~ This is POST request. Received: {"key": "value"} 

#~ You may consider to parse the JSON if you like.

httpd = HTTPServer(('0.0.0.0', 4443), SimpleHTTPRequestHandler)

print(dir(httpd))
httpd.server_name = "SuperServ"

# generate .pem with:
# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
# pwd pa..pa

httpd.socket = ssl.wrap_socket( httpd.socket, keyfile="keys/key.pem", certfile='keys/cert.pem', server_side=True )

httpd.serve_forever()