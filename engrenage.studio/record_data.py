# index of engrenage.studio
# version sept 2023, porting to thenardier.fr

import sys
import time

sys.path.append("/home/na/dev/git/obo/altwww/")
import altcommon


def recordData(timestamp, strHostname, dataname, datavalue ):
    """
    Record received data to disk
    """

        
    o = ""
    if 1:
        o += "DBG: hostname: '%s', dataname: '%s', value: %s, t: %.3f\n" % (strHostname,dataname,datavalue,timestamp)
        
    
    dest = "/var/www/save/webdata.txt" # here we want to save there, even if running as root
    f = open(dest,"a+")
    f.write("%.2f: %s: %s: %s\n" % (timestamp,strHostname,dataname,datavalue) )
    f.close()
        
    o += "data recorded"
    return o
   
def index(req):
    """
    args:
    - h: host
    - dn: dataname
    - dv: data value
    """
    # warning: it search for a </html> to decide if it's html or plain text !!!!
    filename = req.filename
    bDebug = 0
    strMeta = "<meta name='keywords' content='engrenage, engrenage studio,kremlin bicetre,alexandre mazel,alma,aldebaran robotics'>\n<meta name='description' content='Home of engrenage studio, innovation studio'>"
    txt = altcommon.getHtmlHeaderStd("Engrenage","img/ico_engrenage2.png",strMeta)
    txt += "<body><br><center>"
    txt += "<br>"
    txt += "<br>"
    #~ txt += "<p style = 'font-family:georgia,garamond,serif;font-size:56px'>"
    #~ txt += "<img src='img/logo_engrenage.png' width=320px />"
    txt += "record data page"

    
    if bDebug:
        txt += "<p>"
        txt += "host: '%s'<br>\n" % req.hostname
        txt += "filename: '%s'<br>\n" % filename
        txt += "args: '%s'<br>\n" % req.args

    
    dArgs  = altcommon.analyseArgs(req.args)
    
    if bDebug:    
        txt += "dArgs: %s<br>\n" % str(dArgs)
        txt += "</p>"
        
    strHostname = dArgs["h"]
    dataname = dArgs["dn"]
    datavalue = dArgs["dv"]
    if "t" in dArgs:
        timestamp = float(dArgs["t"])
    else:
        timestamp = time.time()
        
    txt += "INF recordData return: <br>"
    txt += recordData(timestamp,strHostname,dataname, datavalue)

    txt += "</html>"
    return txt
# index - end