"""
Pour me lancer en prod:
sudo systemctl restart alexserv.service ; sleep 1 ; sudo systemctl status alexserv.service | more

Pour stopper:
sudo systemctl stop alexserv.service

Pour changer la ligne de commande:
sudo nano /lib/systemd/system/alexserv.service

# activer au demarrage
sudo systemctl enable alexserv.service

# test perf:
wget --no-check-certificate https://obo-world.com/www/agent/data/obo_lightweight.glb -o /tmp/o.glb

After a RPI reboot do:
mkdir /tmp/save/
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import ssl

import gzip
import io
import os
import importlib
import sys
import time
try: from jsmin import jsmin
except: pass

import threading

sys.path.append("./www/") # to help finding js_request, when called from agent/


def writeBuf(theself,buf):
    theself.wfile.write(buf)

def getTimeStamp():
    """

    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    import datetime
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def isFileNotToBeGzip(pathfilename):
    base,ext = os.path.splitext(pathfilename)
    if ext in ['.mp3']:
        return True
    return False

def changeToDefaultIfNotExist( strDir, strOriginalPath, strNewPath="" ):
    """
    add default name if new path not found
    """
    print("DBG: changeToDefaultIfNotExist: testing: '%s', '%s', '%s'" % (strDir, strOriginalPath, strNewPath))

    if strNewPath == "" and os.path.isfile(strDir + strOriginalPath):
        return strOriginalPath
        
    if not os.path.isfile(strDir + strNewPath):
        strNewPath = strOriginalPath + "/index.html"
    if not os.path.isfile(strDir + strNewPath):
        strNewPath = strOriginalPath + "/index.htm"
    return strNewPath


class Access:
    """
    logger for access and referer dedicated to AlexServ
    """
    def __init__(self):
        if os.name != "nt": 
            self.savefilename = "/home/na/logs/webaccess.log"
        else:
            self.savefilename = "c:/logs/webaccess.log"
            
        self.records = []
        
    def save( self ):
        try:
            f = open(self.savefilename,"a+t")
        except FileNotFoundError as err:
            if os.name != "nt": 
                assert(0)
            return
        for r in self.records:
            f.write(";".join(r)+"\n")
        self.records = []
        f.close()
        
    def addVisitor(self, strSiteName,strPage,strRef,strMachine,strIp,strXForward,username):
        stamp = getTimeStamp()
        strSiteName = strSiteName.replace(";",",")
        strPage = strPage.replace(";",",")
        strRef = strRef.replace(";",",")
        strMachine = strMachine.replace(";",",")
        strIp = strIp.replace(";",",")
        strXForward = strXForward.replace(";",",")
        username = username.replace(";",",")
        r = [stamp,strSiteName,strPage,strRef,strMachine,strIp,strXForward,username]
        self.records.append(r)
        self.save()
        
#class Acccess - end

access = Access()
        

class WebFunctionChanger:
    """
    receive all .js and .html and replace function name by f1, f2, ...
    """
    def __init__( self, bVerbose = 0 ):
        self.functionDict = {}
        self.alreadyUsedFunction = set() # very sad: html is loaded first so all call to future js function can't be scrambled!
        self.bVerbose = bVerbose
        
    def printTransTable(self):
        for k,v in self.functionDict.items():
            print("%s=>%s" % (k,v))
        
    def transform(self,s:str) -> str: # if error here, it's because python has been used instead of python3!
        """
        buf
        """
        words = []
        o = ""
        i = 0
        ibegin = 0
        lens = len(s)
        bPrevIsFunction = 0
        sepaFunctionBody = "({"
        while i < lens:
            c = s[i]
            if c in " ,:;.'\"!?-(){}<>+*/=\n":
                if i-ibegin>0:
                    new_word=s[ibegin:i]
                    #~ if self.bVerbose: print("DBG: WebFunctionChanger.transform: new_word: '%s'" % new_word)
                    words.append(new_word)
                    if new_word == "function":
                        bPrevIsFunction = 1
                    elif bPrevIsFunction:
                        bPrevIsFunction = 0
                        if self.bVerbose: print("DBG: WebFunctionChanger.transform: got at %4d function definition: '%s'\ncontext:\n------\n%s\n------" % (i,new_word,s[i-80:i+40]))
                        if new_word in self.alreadyUsedFunction or "run_filter" in new_word: # l'appel a run_filter est du code genere a la volee donc pas trouvable au moment du parse
                            if self.bVerbose: print("DBG: WebFunctionChanger.transform: not changing this one, as already called")
                        else:
                            if new_word not in self.functionDict:
                                new_function_name = "f"+str(len(self.functionDict)+1)
                                if self.bVerbose: print("DBG: WebFunctionChanger.transform: => '%s'" % new_function_name)
                                self.functionDict[new_word] = new_function_name
                                new_word = new_function_name
                            else:
                                print("ERR: redefinition of a function ? context:\n------\n'%s'\n------" % o[-80:])
                                #~ assert(0)
                    else:
                        #~ if self.bVerbose: print("DBG: WebFunctionChanger.transform: is a function to replace ? %s, sepa: '%c'" % (new_word,c))
                        #~ print("dict:\n%s" % str(self.functionDict))
                        if c == '(' or c == ',' or c == ')' or (  i+1<lens and (s[i+1] == '('or s[i+1] == ',' or s[i+1] == ')')  ): # appel de fonction ou fonction passe en parametre de fonction
                            #~ print("seems like function name!")
                            if new_word in self.functionDict:
                                if self.bVerbose: print("DBG: WebFunctionChanger.transform: in place of '%s', using '%s'" % (new_word,self.functionDict[new_word]))
                                new_word = self.functionDict[new_word]
                            else:
                                #~ if self.bVerbose: print("DBG: WebFunctionChanger.transform: adding '%s' to alreadyUsedFunction" % new_word)
                                self.alreadyUsedFunction.add(new_word)
                    o += new_word + c
                    if c in sepaFunctionBody:
                        bPrevIsFunction = 0                    
                else:
                    o += c
                    #~ if self.bVerbose: print("DBG: WebFunctionChanger.transform: c: '%s'" % c) 
                    if c in sepaFunctionBody:
                        bPrevIsFunction = 0
                        
                ibegin = i+1
            i += 1
        if ibegin < i:
            words.append(s[ibegin:i])
        return o
   
# class WebFunctionChanger - end

webFunctionChanger = WebFunctionChanger(bVerbose=1)

if 0:
    strSourceExample = """
    setTimeout( store_referer, 200 );
    function toto(x,y)
    {
        return x+y;
    }
    setTimeout(function() { select_last_req() }, 200);
    toto(3,5)
    function isMobile()
    {
      let check = false;
      (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|te\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
      return check;
    }
    let a = 35;
    function demo()
    {
        let toto = 35;
    }
    <span id="req_created"> <script>demo("Cree le 11.02.2023 a 12h54")</script></span></p>
    let demo = 56;
    setTimeout( demo, 200 );
    function store_referer()
    {
        // une fonction defini apres son appel, on ne doit pas la changer.
    }
    """
    ret  = webFunctionChanger.transform(strSourceExample)
    print("=>\n"+ret)
    exit(1)

class MyServer:
    def __init__(self):
        #~ self.strName = "AlexServ"
        #~ self.strVersion = "0.6"
        self.strName = "Microsoft Azure & Azmar"
        self.strVersion = "5.3.78.4235"
        
        self.loadedFiles = {} # filename => timstamp read, buf

        self.counter = 0
        
        self.bDev = 1
        #~ self.bDev = 0
        
        if os.name == "nt":
            self.bDev = 1
        
        self.bVerbose = 1
        self.bVerbose = 0
        
        self.bOutputIsGzipped = 0
        self.bOutputIsGzipped = 1
        
        self.bUseJsMin = 0
        self.bUseJsMin = 1
        
        self.bUseFunctionTransform = 0
        #~ self.bUseFunctionTransform = 1 # bUseJsMin has to be 1
        
        # bUseFunctionTransform is not working as we have no memory of context: 
        # it works fine, if started first by dashboard
        # but it doesn't work when starting server then going to offer then to dashboard: 
        # some method like store_refererer and companyToLogoName aren't defined
        # surement un probleme de cache
        
        # sauf si on precharge les js !
        # => ca marche !!!
        
        self.dictAlreadyOutputCantLog = {}
        self.logInfo("starting server...")
        
        
    def log( self, s ):
        """
        return name of log file or None on error
        """
        sourcename = "AlexServer"
        import threading
        strMessage = "%s: %s: %s: %s" % (threading.currentThread().ident, getTimeStamp(),sourcename, s)
        
        # output to /var/log/apache2/error.log when called from mod_python
        sys.stderr.write(strMessage + "\n")
        sys.stderr.flush()
        
        if os.name != "nt": 
            fn = "/home/na/logs/%s.log" % sourcename
        else:
            fn = "c:/logs/%s.log" % sourcename
        try:
            f = open(fn,"at")
        except BaseException as err:
            f = None
        
        try:
            if f == None: f = open(fn,"wt")
            f.write(strMessage+"\n")
            f.close()
        except  (FileNotFoundError,PermissionError) as err:
            if sourcename not in self.dictAlreadyOutputCantLog:
                self.dictAlreadyOutputCantLog[sourcename] = True
                print("CANT LOG: %s (err:%s)" % (strMessage,err) )
            return None
        print("LOG: %s" % (strMessage))
        return fn
        
    def logError(self,txt):
        sepa = "-"*50
        filenamelog = self.log("ERR: " + txt + "\n" +  sepa)
        import traceback
        f = open(filenamelog,"at")
        traceback.print_exc(file=f)
        f.write(sepa+"\n")
        f.close()
        traceback.print_exc(file=sys.stdout) # duplicate in std out
        print(sepa)

    def logInfo(self,txt):
        return self.log("INF: " + txt)
        
    def preloadJs(self):
        if len(myServer.loadedFiles) > 0:
            return # already done
        self.loadPage("./vitrine/common.js")
        self.loadPage("./www/dashboard2.js")
        self.loadPage("./www/request.js")
        self.loadPage("./vitrine/header.js")
        self.loadPage("./vitrine/footer.js")
        print("DBG: preloadJs: transTable:")
        webFunctionChanger.printTransTable()
        
        
    def loadPage(self,path):
        if not os.path.isfile(path):
            self.logError("loadPage: file '%s' not found, returning empty" % path)
            return b""
            
        if "spider" in path or "cvs" in path or "save" in path:
            self.logError("loadPage: forbotten to access to file '%s', returning empty" % path)
            return b""
            
        base,ext = os.path.splitext(path)
        #~ bIsJs = self.bUseJsMin and ext == ".js" and "chart" not in base and "pdfjs_build" not in base and "viewpdf" not in base
        bIsJs = self.bUseJsMin and ext == ".js" and "chart" not in base and "pdf.worker" not in base and "viewpdf" not in base and ".min." not in base
        bIsHtml = ext == ".htm" or ext == ".html"
        if self.bVerbose: print("DBG: ext: '%s', bIsJs: %s" % (ext,bIsJs))
        if bIsJs or bIsHtml:
            f = open(path,"rt",encoding="cp1252")
        else:
            f = open(path,"rb")
        buf = f.read()
        f.close()
        
        bDontGzip = isFileNotToBeGzip(path)
        if self.bVerbose and bDontGzip: print("DBG: this file won't be compressed!") 
        
        if bIsJs:
            # eg for dashboard2.js:
            # sans jsmin: compressing 33372B =>7681B
            # avec jsmin: compressing 21531B => 5845B
            # avec jsmin+functonChanger: 5760B
            

            if self.bVerbose: print("DBG: jsminifying %dB..." % len(buf))
            buf = jsmin(buf)
                
            if self.bVerbose: print("DBG: function transforming %dB..." % len(buf))
            if self.bUseFunctionTransform: buf = webFunctionChanger.transform(buf)
            if self.bOutputIsGzipped:
                # txt to bin:
                buf = buf.encode('cp1252')
                
        if bIsHtml:
            if self.bUseFunctionTransform: buf = webFunctionChanger.transform(buf)
            buf = buf.encode('cp1252')
            
        if self.bOutputIsGzipped and not bDontGzip:
            if self.bVerbose: print("DBG: compressing %dB..." % len(buf))
            buf = gzip.compress(buf) # default is best compression: compresslevel=9
            if self.bVerbose: print("DBG: new size: %dB..." % len(buf))
        myServer.loadedFiles[path] = time.time(),buf
        return buf
        

# class MyServer - end

myServer = MyServer()
    
    
    

def decodeBytes(buf):
    #~ decoder = io.BytesIO(buf)
    #~ decoded = decoder.getvalue()
    """
    transform bytes like 0=l&1=%3D&2=d&3=e&4=m&5=o&6=%26&7=p&8=%3D&9=l&10=e&11=t&12=e&13=s&14=t 
    into l=demo&p=letest
    
    NB: ne fonctionnera surement pas sur des gros bouts de donnees TODO en cours
    
    return a params, dictBinary
        params: a string containing name1=value1&name2=value2, eg: l=demo&p=letest
        dictBinary: dictionnary of binary buffer with information related to some fields, eg: cv=filename.pdf will be followed by a dict
        {"cv": [filename, filetype, binary_data]}
    """
    dictBinary = {}
    
    # exemple de donnees recues dans le formulaire visible dans le fichier post_data_received.txt
    #~ print(buf)
    
    print("DBG: decodeBytes: buf first bytes: %d (0x%x), %d(0x%x), %d(0x%x)" % (buf[0],buf[0],buf[1],buf[1],buf[2],buf[2]) )

    if buf[0] != 45 and buf[1] != 45  and buf[2] != 45 : # different de --------- (chr(45) == '_'
        print("INF: decodeBytes: analysing connection data")
        buf = str(buf).strip("'")
        splitted = buf.split("=")
        #~ print(splitted)
        s = ""
        for e in splitted[1:]: # first is 0=
            s += e.split('&')[0]
        decoded = s.replace('%3D','=').replace('%26','&')
    else:
        print("INF: decodeBytes: analysing candidate form data or drop")
        
        # bon j'avoue cette partie la est bien crado
        decoded = ""
        
        strBegin = 'Content-Disposition: form-data; name="'
        strBeginData = 'Content-Type: '
        binBegin = strBegin.encode()
        binBeginData = strBeginData.encode()
        binEnd = '"'.encode()
        
        idx = 0
        idx2 = 0
        while idx < len(buf):
            
            idx = buf[idx2:].find(binBegin)
            if idx == -1:
                break
            idx += idx2 + len(binBegin)
            
            idx2 = buf[idx:].find(binEnd)
            print("idx: %s, idx2: %s" % (idx,idx2))
            if idx2 == -1:
                break
            idx2 += idx
            strName = buf[idx:idx2].decode()
            print("DBG: decodeBytes: strName: '%s'" % strName )
            idx2 += 1 # skip the "
            # next is \r\n\r\nvalue\r\n
            print("buf[idx2:idx2+4]: %s" % buf[idx2:idx2+4])
            strExtraField = ""
            if len(decoded)>0: decoded += '&'
            decoded += strName + "="
            strFilename = "?"
            if buf[idx2] == b';'[0]:
                print("DBG: decodeBytes: got a following field")
                idx3 = buf[idx2:].find(b'\r\n')
                # check idx3 et capture la fin jusqu'a filename
                idx3 += idx2
                strExtraField = buf[idx2+2:idx3].decode()
                print("DBG: decodeBytes: strExtraField: '%s'" % strExtraField )
                strFilenameField = 'filename="'
                idxFilename = strExtraField.find(strFilenameField)
                if idxFilename != -1:
                    idxFilename += len(strFilenameField)
                    idxFilenameEnd = strExtraField[idxFilename:].find('"')
                    strFilename = strExtraField[idxFilename:idxFilename+idxFilenameEnd]
                    print("DBG: decodeBytes: strFilename: '%s'" % strFilename )
                    decoded += strFilename
                else:
                    decoded += strExtraField
                idx2 = idx3
            else:
                print("buf[idx2:idx2+4] (2): %s" % buf[idx2:idx2+4])
                if buf[idx2:idx2+4] != b'\r\n\r\n':
                    print("ERR: decodeBytes: data incomplete (3)? (10 next data: '%s')(%s)" % (buf[idx2:idx2+10].decode(),buf[idx2:idx2+10]))
                    break
                idx = idx2 + 4

                idx2 = buf[idx:].find(b'\r\n')
                if idx2 == -1:
                    print("ERR: decodeBytes: data incomplete (4)? (10 next data: '%s')(%s)" % (buf[idx2:idx2+10].decode(),buf[idx2:idx2+10]))
                    break
                idx2 += idx
                strValue = buf[idx:idx2].decode()
                print("DBG: decodeBytes: strValue: '%s'" % strValue )
                decoded += strValue
                
            idxData = buf[idx2:].find(binBeginData)
            idxNext = buf[idx2:].find(binBegin)
            print("idxData: %s" % idxData )
            print("idxNext: %s" % idxNext )
            if idxNext == -1:
                idxNext = len(buf[idx2:]) # patch pour form_drop: si pas de fin, alors on prend jusqu'a la fin
            if idxData != -1 and idxData < idxNext:
                # on a des datas pour ce champ
                print("DBG: decodeBytes: got data for this field")
                idxData += idx2 + len(binBeginData)
                idx2 = buf[idxData:].find(b'\r\n')
                if idx2 == -1:
                    print("ERR: decodeBytes: data incomplete (5)? (10 next data: '%s')(%s)" % (buf[idx2:idx2+10].decode(),buf[idx2:idx2+10]))
                    break
                idx2 += idxData
                strFileType = buf[idxData:idx2].decode() # style: application/pdf
                print("DBG: decodeBytes: strFileType: '%s'" % strFileType )
                if buf[idx2:idx2+4] != b'\r\n\r\n':
                    print("ERR: decodeBytes: data incomplete (6)? (10 next data: '%s')(%s)" % (buf[idx2:idx2+10].decode(),buf[idx2:idx2+10]))
                    break
                idx1 = idx2+4
                # find the end of binary, how to do that properly ?
                binEndMark = b"\r\n-----------------------------"
                binEndMarkAlt = b"\r\n------WebKitFormBoundary" # ipad de mathieu
                idx2 = buf[idx1:].find(binEndMark)
                if idx2 == -1:
                    try:
                        print("WRN: decodeBytes: data incomplete (7)? (10 next data: '%s')(%s)" % (buf[idx1:idx1+10].decode(),buf[idx1:idx1+10]))
                    except UnicodeDecodeError:
                        print("WRN: decodeBytes: data incomplete (7b)?")
                        
                    #~ break
                    idx2 = buf[idx1:].find(binEndMarkAlt)
                    if idx2 == -1:
                        print("WRN: decodeBytes: data incomplete (8): even using binEndMarkAlt")
                        idx2 = len(buf[idx1:])
                    
                idx2 += idx1
                print("INF: decodeBytes: binary size: %d" % (idx2-idx1))
                dictBinary[strName] = [strFilename,strFileType,buf[idx1:idx2]]
        
                
        
    return decoded,dictBinary
    
#~ print(decodeBytes("0=l&1=%3D&2=d&3=e&4=m&5=o&6=%26&7=p&8=%3D&9=l&10=e&11=t&12=e&13=s&14=t"))
#~ exit(1)

def getRemoteHostEmulated(param=None):
    return "grhe_ndev"
    
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self,request, client_address, server):
        self.server_version = myServer.strName
        self.sys_version = myServer.strVersion
        self.contents_type = "" # to be filled somewhere more or less automatically
        self.nContentsLen = -1
        
        self.bVerbose=1
        self.bVerbose=0

        super().__init__(request, client_address, server)
        
    def end_headers(self):
        self.send_my_headers()
        super().end_headers()
        
    def getContentsType(self):
        # BW: firefox is easy to guess contents type, but oters like chrome require it (or else square in place of svg (but not when opening image in new tab)
        if ".css" in self.path:
            return "text/css"

        if ".js" in self.path:
            return "text/javascript"
            
        if ".html" in self.path: # or "js_offer.py" in self.path:
            return "text/html; charset=cp1252"

        if ".txt" in self.path:
            return "text/plain"
        
        if ".jpg" in self.path or "viewcv.py" in self.path:
            return "image/jpeg"     
            
        if ".svg" in self.path:
            return "image/svg+xml"

        if ".pdf" in self.path:
            return "application/pdf"
            
        return ""

    def send_my_headers(self):
        # attention, ne pas tester avec la fenetre de debug du reseau ouverte, car sinon il cache differemment.
        # memme si desactiver le cache n'est pas cocher il me semble (en tout cas sur AlexServ)
        # ou alors il faut relancer l'onglet?
        
        #~ print("DBG: send_my_headers: path: %s" % self.path)
        if not myServer.bDev:
            # set cache
            if "CGU_obo" in self.path or ".mp3" in self.path or ".svg" in self.path or ".png" in self.path or ".woff" in self.path or ".jpg" in self.path or ".glb" in self.path or ".css" in self.path:
                #~ print("DBG: caching 100 min")
                if self.bVerbose: print("DBG: send_my_headers: setting full cache")
                self.send_header("Cache-Control", "max-age=604800; immutable") # 604800 => 1week 
                
            if (".js" in self.path and not "data_" in self.path ):
                #~ self.send_header("Cache-Control", "max-age=86400; immutable") # 86400 => 1 day
                self.send_header("Cache-Control", "max-age=7200; immutable") # 7200 => 2 h (car on change souvent les js en ce moment)

        if self.contents_type == "":
            self.contents_type = self.getContentsType()
            
        print("DBG: send_my_headers: contents type: %s" % self.contents_type )
        
        if self.contents_type != "":
            self.send_header("Content-Type", self.contents_type)
            
        if self.nContentsLen != -1:
            self.send_header("Content-length", str(self.nContentsLen))
        

            
            
        # attention ne pas mettre en cache les scripts, car meme si les parametres changent, le cache ne sera pas relance!
        if "viewcv.py" in self.path:
            print("%.3f: DBG: setting big cache for viewcv.py" % time.time())
            # ne pas mettre immutable: cela ne le reprendrai pas meme si le parametre change
            
             # 86400 => 1j
              # 864000 => 1j
            #on mettais 1j, on essayera de pas relancer le serveur trop souvent.
            # maintenant on peut mettre 10, grace aux reglages des 2 premiers lettres: on peut relancer toutes les 10min a chaque differentes heures)
            # c'est quand meme bien de pas relancer trop souvent car les scripts renvoient la meme valeur!
            self.send_header("Cache-Control", "max-age=864000")
            
        if myServer.bOutputIsGzipped and not isFileNotToBeGzip(self.path):
            self.send_header("Content-Encoding", "gzip")
            
        #~ cookie = SimpleCookie()
        #~ cookie['a_cookie'] = "Cookie_Value"
        #~ cookie['b_cookie'] = "Cookie_Value2"

        #~ for morsel in cookie.values():
            #~ self.send_header("Set-Cookie", morsel.OutputString())

    def sendCookie(self,name,value,expireInSec=0):
        #~ print("DBG: sendCookie: Send cookies: %s: %s" % (name,value) )
        s = "%s=%s;Path=/" % (name,value)
        if expireInSec != 0:
            s += "; Max-Age=%d" % expireInSec
        self.send_header("Set-Cookie", s)
        
    def getCookie(self,name, defaultValue = ""):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        #~ print("DBG: getCookie: cookies: %s" % cookies)
        try:
            cook = cookies[name]
        except KeyError as err:
            cook = type('', (), {})()
            cook.value = defaultValue
            
        #~ print("DBG: getCookie: %s => %s" % (name,cook) )
        return cook
        
    def fillReq(self,req):
        """
        store classical information in req for compat with mod_python
        """
        req.hostname = "obo-world.com"
        req.status = ""
        req.server = ""
        req.filename = ""
        req.construct_url = ""
        req.document_root = ""
        req.path_info = ""
        req.uri = ""
        #~ req.get_remote_host = lambda  : ""
        #~ req.get_remote_host = lambda  x: "get_remote_host_todo"
        req.get_remote_host = getRemoteHostEmulated
        req.headers_in = {}
        req.headers_in['Host'] = "obo-world_aserv.com"
        req.headers_in['User-Agent'] = self.strUserAgent
        req.headers_in['referer'] = self.strReferer
        req.headers_in['X-Forwarded-For'] = self.strXForwardFor
        print("DBG: fillReq: self.client_address[0]: %s" % self.client_address[0] )
        req.headers_in['RemoteIP'] =  self.client_address[0] # eg: 92.184.106.142 is orange
        
    def preloadFile(path):
        self.path = path
        self.handleReq(0)
        
    def analyseRequestHeader(self):
        if self.bVerbose: print("DBG: analyseRequestHeader:\n"+str(self.headers))

        # eg:
        """
DBG: analyseRequestHeader:
Host: www.obo-world.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Referer: https://www.google.com/
DNT: 1
Upgrade-Insecure-Requests: 1
X-Forwarded-For: 192.168.0.100
X-Forwarded-Host: www.obo-world.com
X-Forwarded-Server: obo-world.com
Connection: Keep-Alive

# un robot:
Host: obo-world.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36
X-Forwarded-For: 138.246.253.24
X-Forwarded-Host: obo-world.com
X-Forwarded-Server: obo-world.com
Connection: Keep-Alive

#depuis une page:
Host: www.obo-world.com
User-Agent: Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-A528B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/19.0 Chrome/102.0.5005.125 Mobile Safari/537.36
DNT: 1
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Referer: http://www.obo-world.com/vitrine/
Accept-Encoding: gzip, deflate
Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7
X-Forwarded-For: 92.184.106.143
X-Forwarded-Host: www.obo-world.com
X-Forwarded-Server: obo-world.com
Connection: Keep-Alive

#depuis presence:
Host: obo-world.com
Connection: keep-alive
User-Agent: Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-A528B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/19.0 Chrome/102.0.5005.125 Mobile Safari/537.36
DNT: 1
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: script
Referer: https://obo-world.com/send_presence.py
Accept-Encoding: gzip, deflate, br
Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7


        """
        self.strReferer = ""
        self.strUserAgent = ""
        self.strXForwardFor = ""
        
        h = str(self.headers)
        lines = h.split("\n")
        for li in lines:
            if li == "": continue
            try:
                idx = li.index(":")
                if idx == -1: continue
                s = li[:idx]
                v = li[idx+1:].strip()
                s = s.lower()
                if s == "referer":
                    self.strReferer = v
                elif s == "user-agent":
                    self.strUserAgent = v
                elif s == "x-forwarded-for":
                    self.strXForwardFor = v
            except BaseException as err:
                print("DBG: analyseRequestHeader: li: '%s', err: %s" % (li,err))
        
        if self.bVerbose: print("DBG: analyseRequestHeader: strUserAgent: '%s'" % self.strUserAgent )
        if self.bVerbose: print("DBG: analyseRequestHeader: strReferer: '%s'" % self.strReferer )
        if self.bVerbose: print("DBG: analyseRequestHeader: strXForwardFor: '%s'" % self.strXForwardFor )
        
    def handleReq(self,bFromPost):
        timeBegin = time.time()
        bVerbose = 1
        bVerbose = 0
        bVerbose = self.bVerbose
        
        #~ cookies = SimpleCookie(self.headers.get('Cookie'))
        #~ print("cookies: %s" % cookies )

        
        if bVerbose or 1: print("="*60)
        if bVerbose or 1: print("%.3f: DBG: handleReq: path: '%s'" % (time.time(),self.path))
        self.analyseRequestHeader()
        
        # strSiteName,strPage,strRef,strMachine,strIp,strXForward,username
        try:
            cookie_access_token = self.getCookie("access_token","unk")
            if bVerbose: print("cookie_access_token:%s" % cookie_access_token)
            if bVerbose: print("cookie_access_token.value:%s" % cookie_access_token.value)
            username = str(cookie_access_token.value).split("__")[0]
            if bVerbose: print("username: %s" % username)
        except IndexError as err: username = "unke"
        strHostname = self.headers.get('Host')
        access.addVisitor(strHostname,self.path,self.strReferer,self.strUserAgent,"",self.strXForwardFor,username)
        
        if "/?fbclid=" in self.path:
            # cas particulier depuis instagram, ou le path vaut juste /?fbclid=PAAaahA0zpEcmmqJKLfG5i9JZuo9xIEOnBjUpi4X_EmBUlQKR-rsLNHjgSxEA
            self.path = "index.html"
            
        if "engrenage.studio" in strHostname:
            print("DBG: got eng")
            strDir = "./altwww/engrenage.studio/"
            if self.path == '/':
                self.path = "/eng_index.py"
            else:
                # comme on  ne peut pas avoir 2 fichiers de meme nom (index.py, on va generer des noms de dossiers parent_index
                print("DBG: path: %s" % self.path )
                strLast = os.path.basename(self.path)
                print("DBG: strLast: %s" % strLast )
                if "." not in strLast:
                    strNewPath = self.path + "/" + strLast + "_index.py"
                    self.path = changeToDefaultIfNotExist(strDir,self.path,strNewPath)
            self.path = strDir + self.path

            
        if "human-machine-interaction.org" in strHostname:
            print("DBG: got hmi")
            print("DBG: path: %s" % self.path )
            strDir = "./altwww/human-machine-interaction.org/"
            if self.path == '/':
                self.path = "/index.htm"
            else:
                self.path = changeToDefaultIfNotExist(strDir,self.path)
            self.path = strDir + self.path
            
        if "wellbeing.paris" in strHostname:
            print("DBG: got wellbeing")
            print("DBG: path: %s" % self.path )
            if self.path == '/':
                self.path = "/index.html"
            self.path = "./altwww/wellbeing.paris/" + self.path
            
        
            
        if "itw." == strHostname[:4]:
            print("DBG: got itw.")
            if "/?id=" == self.path[:5]:
                print("DBG: got request for an interview")
                self.path = "./www/agent/index.html"+self.path[1:]
            elif "/sound/" == self.path[:7] or "/getdiag" == self.path[:8]:
                self.path = "./www/"+self.path
            elif "/vitrine/" in self.path:
                pass
            else:
                self.path = "./www/agent/."+self.path
        else:
            if "/getdiag" == self.path[:8]:
                self.path = "./www/"+self.path
            
            
            
        if self.path == '/':
            self.path = "index.html"
            #~ self.path = "/vitrine/index.html"
        if self.path == '/vitrine/':
            self.path = "/vitrine/index.html"
            
        if "/vitrine/" == self.path[:9]:
            self.path = "." + self.path
            
        if "/www/" == self.path[:5]:
            self.path = "." + self.path

        if "/sound/" == self.path[:7]:
            self.path = "./www" + self.path

        if "/index.py" == self.path[:9]:
            #~ self.path = "./www" + self.path
            self.path = "./files_in_apache_root_copy/" + self.path
            
        if "/cvs_blurred" == self.path[:12]:
            self.path = "/home/na/cvs/cvs_pool_blurred" + self.path.replace("/cvs_blurred","")

        if "/o?" == self.path[:3]:
            self.path = "./vitrine/offers.htm?o=" + self.path[3:]
            print("DBG: handleReq: offer shortcut => exploding real address to '%s'" % self.path)
            
        # quand on vient de o, ensuite tout est pourri: /img/   /header.js ...
        if "/" == self.path[0]:
            self.path = "./vitrine/" + self.path
            
        if "/index.py" == self.path[:9]:
            self.path = "./www" + self.path

            
        self.path = self.path.replace("%20"," ")
        if bVerbose or 1: print("DBG: handleReq: self.path(2): %s" % self.path)
        
        req = type('', (), {})()
        self.fillReq(req)
        req.server = myServer
        req.handler = self
        req.form = {} # for compat and post
        req.read = lambda  : "DBG: req.read do nothing, it's just here for compat."
        
        idx_interro = self.path.find('?')
        params = ""
        if idx_interro != -1:
            params = self.path[idx_interro+1:]
            self.path = self.path[:idx_interro]
            
        if bFromPost:
            if bVerbose or 1: print("DBG: handleReq: post received...")
            content_length = int(self.headers['Content-Length'])
            if bVerbose or 1: print("DBG: handleReq: post: content_length: %s" % content_length )
            body = self.rfile.read(content_length)
            if bVerbose or 1: print("DBG: handleReq: post: body: %s" % body[:300] )
            decoded_body_params, dictBinary = decodeBytes(body)
            if bVerbose or 1: print("DBG: handleReq: post: decoded_body: %s - dictBinary len: %s, keys: %s" % (decoded_body_params,len(dictBinary),str(dictBinary.keys()) ) )
            if len(params)>0 and params[-1] != '&': params += '&'
            params += decoded_body_params
            for k,v in dictBinary.items():
                req.form[k] = type('', (), {})()
                req.form[k].filename = v[0]
                req.form[k].value = v[2] # le binary
            # put all params in form also for compat (argh)
            sys.path.append("./vitrine")
            import common_vitrine # argh d'importer ca ici
            argsfrompost = common_vitrine.analyseArgs(params, "")
            for k,v in argsfrompost.items():
                if k not in req.form:
                    req.form[k] = v
                
        if bVerbose: print("DBG: handleReq: self.path(3): %s" % self.path)
        
        
        self.send_response(200)
        
        #~ self.wfile.write(b'Hello, world!')
        # attention, on ne peut pas avoir 2 fichiers python avec le meme nom !!!
        if ".py" == self.path[-3:]:
            if bVerbose: print( "DBG: handleReq: python script!" )
            req.args = params
            pathname, filename = os.path.split(self.path)
            filename_without_ext = filename.replace(".py","")

            if bVerbose: print( "DBG: handleReq: self.path: %s" % self.path )
            if bVerbose: print( "DBG: handleReq: req.args: %s" % req.args )
            if bVerbose: print( "DBG: handleReq: filename: %s" % filename )
            #~ mod = importlib.import_module(self.path,filename)
            sys.path.append(pathname)
            mod = importlib.import_module(filename_without_ext) # too bad we can't pass globals=globals()
            
            # force a reload if in dev:
            if myServer.bDev and 0: # attention ca ne fonctionne pas de recharger pour les trucs sans save comme le imageviewerscrambler
                print("WRN: reloading %s" % filename_without_ext)
                importlib.reload(mod)
            
            timeBegin = time.time()
            
            if myServer.bDev:
                ret = mod.index(req) # crash to see errors
            else:                
                try:
                    ret = mod.index(req)
                except BaseException as err:
                    myServer.logError("During execution of %s, err: %s" % (self.path,err))
                    return
            
            if myServer.bDev:
                bar = "#"*40
                print(bar)
                print("# python answer:")
                if ret == None: 
                    print("# set to 1")
                    ret = "1"
                else:
                    if type(ret)==str or type(ret)==bytes:
                        print(ret[:400])
                        if(len(ret)>400): print("...")
                    else:
                        print("WRN: handleReq: type of ret is different: %s" % type(ret))
                        print("%s"%ret)
                print(bar)
                
            self.contents_type = ""
            if type(ret)==str and ("<html>" == ret[:6].lower() or "<!doctype html>" == ret[:15].lower()):
                if bVerbose: print("DBG: handleReq: setting contents type to html")
                self.contents_type = "text/html; charset=cp1252"
            
            print( "%.3f: DBG: handleReq: python executed in %.2fs" % (time.time(),time.time()-timeBegin) )
                
            try:
                binret = ret.encode('ascii')
            except UnicodeEncodeError as err:
                binret = ret.encode('utf-8')
            except AttributeError as err:
                # when ret is already binary, there's no encode method
                binret = ret
                
            if myServer.bOutputIsGzipped:
                binret = gzip.compress(binret)
                
            self.end_headers()
            self.wfile.write(binret)
            
            if bVerbose: print("%.3f: DBG: done (python) in %.2fs (then sending back?)\n" % (time.time(),time.time()-timeBegin) )
            return
            
        
        bMustLoad = False
        try:
            
            #~ buf = self.loadedFiles[self.path]
            filestamp,buf = myServer.loadedFiles[self.path]
            print("DBG: handleReq: hit cache success for '%s'" % self.path)
            if myServer.bDev:
                # check file hasn't changed on disk
                if filestamp < os.path.getmtime(self.path):
                    bMustLoad = True
            
        except KeyError:
            bMustLoad = True
            
        if bMustLoad:
            print("%.3f: DBG: real loading of %s" % (time.time(),self.path))
            try:
                buf = myServer.loadPage(self.path)
            except FileNotFoundError:
                myServer.logError("file not found: '%s" % self.path)
                return
        
        
        self.nContentsLen = len(buf) # mostly for duration of mp3
        
        self.end_headers()
        if bVerbose or 1: print("%.3f: DBG: writing..." % time.time())   
        
        print("main thread (0): %s" % (threading.get_ident()))
        
        if 0:
            # essai de threader mais ca fonctionne pas: le fil de l'execution ne continue pas dans le bon thread
            print("main thread (1): %s" % (threading.get_ident()))
            thread = threading.Thread(target=writeBuf,args=(self,buf))
            thread.start()
            print("main thread (2): %s" % (threading.get_ident()))
            self.wfile.close() # cut the socket so the main thread stop using it
            return;
        
        try:
            self.wfile.write(buf)
        except BrokenPipeError as err:
            print("ERR: during writing: bMustLoad: %s, len buf: %s err: %s" % (bMustLoad,len(buf), err)  )
            print("Retrying...")
            self.wfile.write(buf)
            
        if bVerbose or 1: print("%.3f: DBG: done in %.2fs (then sending back?)\n" % (time.time(),time.time()-timeBegin) )
        
    # func  handleReq - end

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
        
        return self.handleReq(0)

        
        
        # untested:
        # cf https://blog.anvileight.com/posts/simple-python-http-server/
    def do_POST(self):
        #~ content_length = int(self.headers['Content-Length'])
        #~ body = self.rfile.read(content_length)
        #~ self.send_response(200)
        #~ self.end_headers()
        #~ response = BytesIO()
        #~ response.write(b'This is POST request. ')
        #~ response.write(b'Received: ')
        #~ response.write(body)
        #~ self.wfile.write(response.getvalue())
        return self.handleReq(1)
        

#~ The request body can be accessed via self.rfile. It is a BufferedReader so read([size]) method should be executed in order to get the contents. Note, that size should be explicitly passed to the function, otherwise the request will hang and never end.

#~ This is why obtaining content_length is necessary. It could be retrieved via self.headers and converted into an integer. An example above just prints back whatever he receives, like follows:

#~ http http://127.0.0.1:8000 key=value
#~ HTTP/1.0 200 OK
#~ Date: Sun, 25 Feb 2018 17:46:06 GMT
#~ Server: BaseHTTP/0.6 Python/3.6.1

#~ This is POST request. Received: {"key": "value"} 

#~ You may consider to parse the JSON if you like.


# class SimpleReq... - end

#~ from threading import Thread
#~ from SocketServer import ThreadingMixIn

from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        message =  threading.currentThread().getName()
        print(threading.get_ident())
        self.wfile.write(message.encode("ascii"))
        self.wfile.write('\n')
        return

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass
    daemon_threads = True
    #~ daemon_threads = False
    
    #~ def __init__(self, *args, **kwargs) -> None:
        #~ super().__init__(*args, **kwargs)
        #~ self.ready = 1
        
    #~ def service_actions(self):
        #~ if self.ready: return
        #~ print("%.3f: DBG: service_actions thread: %s" % (time.time(),threading.get_ident()))
        #~ self.ready = 1
        
    #~ def handle(self):
        #~ self.ready = 0
        #~ super().handle()

def runServer(nPort,bThreaded=False):
    
    myServer.preloadJs()

    print("#"*40)
    print("INF: launching server binded to %d" % nPort )


    if not bThreaded:
        httpd = HTTPServer(('0.0.0.0', nPort), SimpleHTTPRequestHandler)
    else:
        httpd = ThreadingHTTPServer(('0.0.0.0', nPort), SimpleHTTPRequestHandler)

    #~ print(dir(httpd))
    httpd.server_name = "SuperServ"
    httpd.timeout = 60*10 # 10 min !!! (default is 30sec) (utile pour uploader des gros fichiers) (j'ai reussi a uploader un fichier de 130mb, une video depuis mon telephone,, ca a pris 2-3min)

    # generate .pem with:
    # openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
    # pwd pa..pa

    # generate key without pass:
    # openssl pkey -in keys/key.pem -out keys/key_without_pass.pem
    #~ httpd.socket = ssl.wrap_socket( httpd.socket, keyfile="keys/key.pem", certfile='keys/cert.pem', server_side=True )
    if nPort != 80:
        # ssl
        #~ httpd.socket = ssl.wrap_socket( httpd.socket, keyfile="keys/key_without_pass.pem", certfile='keys/cert.pem', server_side=True )
        httpd.socket = ssl.wrap_socket( httpd.socket, keyfile="/etc/letsencrypt/live/itw.obo-world.com/privkey.pem", certfile='/etc/letsencrypt/live/itw.obo-world.com/cert.pem', server_side=True )

    httpd.serve_forever()

if __name__ == "__main__":
    
    """
    Voir les ports ouverts:
    sudo lsof -i -P -n | grep LISTEN
    sudo fuser 80/tcp -k
    """
    runServer(80)
