import os
import subprocess
import time
import threading

def ping(hostname, bVerbose=False):
    #~ print( "INF: ping: pingging '%s'" % hostname )
    
    if os.name == "nt":
        param = "-n"
    else:
        param = "-c"
        
    command = ["ping", param, "1", hostname]
    outfilename = "/tmp/out_%s_%s.txt" % (time.time(), threading.get_ident())
    outfile = open(outfilename, "wt")
    ret = subprocess.call(command, stdout=outfile)
    outfile.close()
    outfile = open(outfilename, "rt")
    buf = outfile.read()
    #~ print("DBG: ping: buf: %s" % buf)
    outfile.close()
    
    os.unlink(outfilename)
    
    #~ return "perte 0%" in buf
    bSuccess = not "Impossible de joindre" in buf
    if bVerbose:
        if bSuccess: print("INF: ping: %s: success !!!" % hostname)
    return bSuccess
    
    
def pinglocal(strMask = "192.168.0."):
    bMultiThread = 1 # works nicely on windows!
    if bMultiThread:
        listThread = []
    for i in range(1,255):
        hostname = strMask + str(i)
        if not bMultiThread:
            # monothread
            ret = ping(hostname)
            if ret:
                print("INF: %s: success !!!" % hostname)
        else:
            # mt
            t = threading.Thread(target=ping, args=(hostname,True))
            t.start()
            listThread.append(t)
    
    if bMultiThread:
        #~ for thread in threading.enumerate(): #ne fonctionne pas
        for thread in listThread:
            thread.join()
        
        
pinglocal("192.168.1.")