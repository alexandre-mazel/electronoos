# index of engrenage.studio
# version sept 2023, porting to thenardier.fr

import sys
sys.path.append("/home/na/dev/git/obo/altwww/")
import altcommon

   
def runCommandGetResults( strCommand ):
    strFilename = "/tmp/" + str(time.time())
    os.system(strCommand + " > " + strFilename )
    f = open(strFilename, "rt")
    buf = f.read()
    f.close()
    os.remove(strFilename)
    return buf

def wake( strComputerName ):
    dComputer = {
        "xenia": ("2C:F0:5D:9F:BF:DE","192.168.0.45"),
        "champion1": ("2C:F0:5D:9F:BF:DE","192.168.0.45")

        }
        
    if strComputerName == None:
        strComputerName,info = dComputer.items()[0]
    else:
        try:
            info = dComputer[strComputerName.lower()]
        except:
            return "ERR: Computer '%s' is unknown<br>\n" % strComputerName
    buf = runCommandGetResults( "nmap -sP %s" % info[1])
    bIsDown = "Note: Host seems down." in buf
    strUpness = "up"
    if bIsDown: strUpness = "down"
    strOut = "Computer '%s' is %s<br>\n" % (strComputerName, strUpness)
    if bIsDown: 
        strOut += "Waking it...<br>\n"  
        os.system("wakeonlan -i %s %s" % (info[1],info[0]) )
        time.sleep(0.5)
        os.system("wakeonlan %s" % info[0] ) # try another way, just in case
    return strOut
    
def generateRotationCode(  filename ):
    txt = """
    <!-- 
        A nice slow and magnificient rotating image object, just for you, happy copy-paster !
        (c) A.Mazel 2022
    -->
    <div>
    <canvas id="canvas" width=320 height=320></canvas>
    </div>
    <script>
        
    var image=document.createElement("img");
    image.onload=function(){
        ctx.drawImage(image,canvas.width/2-image.width/2,canvas.height/2-image.width/2);
    }
    image.src="IMG_FILENAME";
        
    function drawRotated(ctx,degrees){

        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.save();
        ctx.translate(canvas.width/2,canvas.height/2);
        ctx.rotate(degrees*Math.PI/180);
        ctx.drawImage(image,-image.width/2,-image.width/2);
        ctx.restore();
    }
    
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext("2d");
    var degrees = 1;
    function rotate(){
        drawRotated(ctx,degrees);
        degrees += 0.2;
        window.setTimeout(rotate, 20);
    }
    window.setTimeout(rotate, 100);
    </script>
    """
    txt = txt.replace( "IMG_FILENAME", filename )
    return txt
    
def getTemperatureFrom1wire(strDeviceID):
    """
    open w1 devices and extract temperature, return it in degree Celsius
    find /sys/bus/w1/devices/ -name "28-*" -exec cat {}/w1_slave \; | grep "t=" | awk -F "t=" '{print $2/1000}'

    """
    try:
        f = open("/sys/bus/w1/devices/%s/w1_slave" % strDeviceID,"rt")
        lines = f.readlines(2)
        t = lines[-1].split("t=")[-1]
        t = int(t)/1000.
        #~ t -= 1.5 # overheat
    except BaseException as err:
        t = -100
    return t

   
def index(req):
    """
    """
    # warning: it search for a </html> to decide if it's html or plain text !!!!
    filename = req.filename
    bDebug = 0
    strMeta = "<meta name='keywords' content='engrenage, engrenage studio,kremlin bicetre,alexandre mazel,alma,aldebaran robotics'>\n<meta name='description' content='Home of engrenage studio, innovation studio'>"
    txt = altcommon.getHtmlHeaderStd("Thenardier","img/ico_thenardier.png",strMeta)
    txt += "<body><br><center>"
    txt += "<br>"
    txt += "<br>"
    #~ txt += "<p style = 'font-family:georgia,garamond,serif;font-size:56px'>"
    #~ txt += "<img src='img/logo_engrenage.png' width=320px />"
    txt += "<p style = 'font-family:calibri;font-size:56px'>"
    txt += "L &nbsp; a &nbsp;  &nbsp; M &nbsp; a &nbsp; i &nbsp; s &nbsp; o &nbsp; n &nbsp;  &nbsp; d &nbsp; e &nbsp; s &nbsp;  &nbsp; T &nbsp; H &nbsp; E &nbsp; N &nbsp; A &nbsp; R &nbsp; D &nbsp; I &nbsp; E &nbsp; R<br>"
    txt += "</p>"
    txt += "<p style = 'font-family:calibri;font-size:40px'>"
    #~ txt += "<p style = 'font-family:georgia,garamond,serif;font-size:40px'>"
    #~ txt += "<I>La Maison des THENARDIER</I>"
    txt += "</p>"

    txt += "<i>Bienvenue sur cette modeste contribution &agrave; l'oeuvre d'Emile Zola.</i>"

    if bDebug:
        txt += "<p>"
        txt += "host: '%s'<br>\n" % req.hostname
        txt += "filename: '%s'<br>\n" % filename
        txt += "args: '%s'<br>\n" % req.args

    
    dArgs  = altcommon.analyseArgs(req.args)
    
    if bDebug:    
        txt += "dArgs: %s<br>\n" % str(dArgs)
        txt += "</p>"
        
    for k,v in dArgs.items():
        if k.lower() == 'wake':
            retTxt = wake(v)
            txt += retTxt
            
        
    txt += "</html>"
    return txt
# index - end