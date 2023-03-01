import os
import sys
import time

sys.path.append( os.path.dirname(__file__) + "/../alex_pytools/" )
import misctools

global_strPassword = misctools.getEnv("PUBLAC_PWD")
#~ print("DBG: using passwd: '%s'" % global_strPassword )

def transfer( path, filename, extra_remove_folder = "" ):
    """
    extra_remove_folder: specify another path on the remote computer
    """
    global global_strPassword
    if not os.path.isfile("c:\exe\pscp.exe"):
        print("ERR: pscp not present")
        return False
    src = path + filename
    # echo y |  scp ... will say yes in a new computer asking for a key update
    ret = os.system("echo y | c:\exe\pscp -pw %s \"%s\" publac@robot-enhanced-education.org:/home/publac/received/%s" % (global_strPassword,src,extra_remove_folder))
    return ret==0

def move_download(strDownloadPath = "", strSpecificFolder = ""):
    """
    move all files from download folder to another computer.
    - strSpecificFolder: copy file from and into a specific folder, eg: "lki/"
    """
    bVerbose = 1
    bVerbose = 0
    
    if strDownloadPath == "":
        #~ strDownloadPath = os.getlogin()
        strDownloadPath = os.environ['USERPROFILE']
        strDownloadPath += os.sep + "Downloads" + os.sep
        
    print("INF: move_download: strDownloadPath: '%s'" % strDownloadPath )
    print("INF: move_download: strSpecificFolder: '%s'" % strSpecificFolder )
    
    strDownloadPath += strSpecificFolder
    
    listFiles = os.listdir(strDownloadPath)    
    listFiles = sorted(listFiles, key=lambda x: os.path.getmtime(strDownloadPath+x),reverse=True)
    
    for f in listFiles:
        body,ext = os.path.splitext(f)
        extWanted = [".pdf", ".doc", ".docx", ".jpg"]
        if "lki" in strSpecificFolder:
            extWanted.extend([".txt"])
        if ext not in extWanted:
            continue
        absf = strDownloadPath + f
        modtime = os.path.getmtime(absf)
        age = time.time() - modtime
        if age < 60:
            # this file was modified less than 1 min
            if bVerbose or 1: print("DBG: move_download: %s: skipping: too young (%.1fs)" % (ascii(f),age) )
            continue
            
        if age > 60*60*24*31:
            # this file was modified more than 1 month
            if bVerbose: print("DBG: move_download: %s: skipping: too old (%.1f jour(s))" % (ascii(f),age/60/60/24) )
            continue
            
        if age > 60*60*24*7:
            # this file was modified more than 1 week
            if bVerbose: print("DBG: move_download: %s: skipping: too old (%.1f jour(s))" % (ascii(f),age/60/60/24) )
            continue
            
        print("INF: move_download: moving age %.1fs: '%s'" % (age,ascii(f)))
        bSuccess = transfer(strDownloadPath,f,strSpecificFolder)
        print("INF: success: %s" % bSuccess )
        if bSuccess:
            dst = strDownloadPath + os.sep + "moved_files" + os.sep
            try: os.makedirs(dst)
            except FileExistsError as err: pass
            try: 
                os.rename(absf,dst+f)
            except FileExistsError as err: 
                cpt = 1
                body,ext = os.path.splitext(f)
                while os.path.isfile(dst+body+("__%04d"%cpt)+ext):
                    cpt += 1
                os.rename(absf,dst+body+("__%04d"%cpt)+ext)
    
    print("INF: move_download: finished")


def loop_move_download():
    while 1:
        move_download()
        move_download("","lki/")
        time.sleep(60*1)
    

#~ ret = os.system("c:\exe\pscp -pw ??? c:/tmp/a.txt publac@robot-enhanced-education.org:/home/publac/")
#~ print("ret: %s" % ret )
#~ if ret == 0:
    #~ print("Success !!!" )
    
loop_move_download()