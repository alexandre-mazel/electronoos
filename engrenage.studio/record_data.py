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
    
    // test me with:
    http://engrenage.studio/record_data.py?dn=test&dv=421
    http://engrenage.studio/record_data.py?dn=test&dv=421&dn2=test2&dv2=666.42
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
    txt += "Record data page<br>"

    
    if bDebug:
        txt += "<p>"
        txt += "host: '%s'<br>\n" % req.hostname
        txt += "filename: '%s'<br>\n" % filename
        txt += "args: '%s'<br>\n" % req.args

    
    dArgs  = altcommon.analyseArgs(req.args)
    
    if bDebug:    
        txt += "dArgs: %s<br>\n" % str(dArgs)
        txt += "</p>"
        
    try:
        strHostname = dArgs["h"]
    except KeyError as err:
        strHostname = "Unknown host"
        
    if "dn" not in dArgs or "dv" not in dArgs:
        txt += "ERROR: Wrong format (1)<br>"
        txt += "Args: %s" % str(dArgs)
        
        return txt
                
    try:
        dataname = dArgs["dn"]
    except KeyError as err:
        txt += "ERROR: Wrong format (2): no name"
        return txt
        
    datavalue = dArgs["dv"]
    if "t" in dArgs:
        timestamp = float(dArgs["t"])
    else:
        timestamp = time.time()
        
    txt += "INF: recordData for '%s' return: <br>" % dataname
    txt += recordData(timestamp,strHostname,dataname, datavalue) + "<br>"
    
    if "dn2" in dArgs:
        # handle optionnal datanames and values, eg: dn2, dv2,  dn3, dv3, ...
        strTemplateName = "dn%d"
        strTemplateValue = "dv%d"
        txt += "INF: optionnal datas received... <br>"
        nNumVar = 2
        while strTemplateName % nNumVar in dArgs:
            dataname = dArgs[strTemplateName % nNumVar]
            datavalue = dArgs[strTemplateValue % nNumVar]
            txt += "INF:   recordData for '%s' return: <br>" % dataname
            txt += recordData(timestamp,strHostname,dataname, datavalue) + "<br>"
            nNumVar += 1

    txt += "</html>"
    return txt
# index - end