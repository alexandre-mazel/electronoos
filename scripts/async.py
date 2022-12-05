import os
import shutil
import sys
import time

def getThisModulePath():
        try:
            strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        except KeyError as err:
            strLocalPath = ""
        if strLocalPath == "": strLocalPath = "."
        if strLocalPath[-1] != os.sep:
            strLocalPath += os.sep
        return strLocalPath

sys.path.append( getThisModulePath()+"../alex_pytools/")
from stringtools import timeToStr, sizeToStr
from misctools import timeToString # amusant, on a les deux, arf!

def isDirMark(c):
    return c == '/' or c == '\\'
    
def get_last_folder(path):
    """
    c:/toto/tutu/ => tutu
    """
    idx1 = path[:-1].find('/')
    idx2 = path[:-1].find('\\')
    return path[max(idx1,idx2):].replace('/','').replace('\\','')

def isInWindir(path):
    windir = os.getenv("windir").replace(os.sep,'/').lower()
    path = os.path.abspath(path).replace(os.sep,'/').lower()
    #~ print("DBG: isInWindir: windir: '%s'" % windir)
    #~ print("DBG: isInWindir: path: '%s'" % path)
    ret = path[:len(windir)]==windir
    #~ print("DBG: isInWindir: ret: '%s'" % ret)
    #~ if "c:\windows" in path:
        #~ exit(0)
    return ret
    
def handle(s):
    """
    handle error message, exiting if critical
    """
    s = str(s)
    if "No space left" in s:
        print("INF: handle: fatal message: can't be ignored.")
        exit(-100)
    
def _sync(src,dst,bReverseOrder=False,bDryRun=False,bVerbose=False):
    """
    synchronise 2 folders: 
      make sure all in src will be copied in dst, 
      but extra file in dst won't be erased.
      So renaming one file in src will leave original name in dst
    
    Retourne le nbr de fichier dans la src, la taille totale, le nbr de dossier cree, nbr de fichier copie dans dst, (le nombre qui etait absent et le nombre qui devait etre mis a jour)
    
    - src et dst doivent finir par un os.sep
    - bReverseOrder: start by last folder in alphabetical orders
    """
    bDoIt = not bDryRun

    #~ bVerbose = 1
    #~ bVerbose = 0
    bVerboseFolder = 1
    bVerboseFile = 0

    if not isDirMark(src[-1]): src += os.sep
    if not isDirMark(dst[-1]): dst += os.sep
    
        
    nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied = 0,0,0,0,0,0,0
        
    last_folder = get_last_folder(src).lower()
    #~ if bVerbose: print("DBG: sync: last_folder:'%s'\n\n" % last_folder)
    
    #~ (isInWindir(src) and last_folder.lower() in ["security",  "system32", "cache_data", "windowsapps","boot","temp"] )
    if (
        last_folder == "$recycle.bin"
        or (isInWindir(src))
        or last_folder == "tmp"
        or last_folder == "temp"
        or last_folder == "program files"
        or last_folder == "program files (x86)"
         # specific to my computer:
        #~ or last_folder == "flutter"
        #~ or last_folder == "ft saison 1"
        #~ or last_folder == "zfilms"
        #~ or last_folder == "harfang3d"
    ):
        strPadding = " "*(78-len(src))
        print("WRN: skipping folder: '%s' %s" % (src,strPadding))
        return nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied
        
    
    if not os.path.isdir(dst):
        if bDoIt: 
            if bVerbose and bVerboseFolder: print("DBG: sync: creating %s" % dst)
            os.mkdir(dst)
        elif bVerbose and bVerboseFolder: print("DRY: would create folder '%s'" % dst)
        nbr_folder_created += 1
        
    try:
        listSrc = os.listdir(src)
    except PermissionError as err:
        print("ERR: access error skipping folder : '%s'" % src)
        return nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied
    listSrc = sorted(listSrc,reverse=bReverseOrder)
    for f in listSrc:
        if (nbr % 67)==0: # un nombre premier sympa, mais pas trop grand
            out_src = src
            if len(out_src)>65:
                out_src = "..." + out_src[-62:]
                strPadding = ""
            else:
                strPadding = " " * (65-len(out_src))
            print('processed files: %s: %9d (%d)'%(out_src,nbr,nbr_copied) + strPadding, end="\r")  # 1s pour 10000 affichage!
        absf = src + f
        absf2 = dst + f
        if os.path.isdir(absf):
            if not os.path.isdir(absf2):
                if bDoIt: 
                    if bVerbose  and bVerboseFolder: print("DBG: sync: creating %s" % absf2)
                    os.mkdir(absf2)
                elif bVerbose  and bVerboseFolder: print("DRY: would create folder '%s'" % absf2)
                # got this error: OSError: [WinError 1392] Le fichier ou le repertoire est endommage et illisible: 'e:\\copie_vaio\\Alexandre\\mirror_0d\\wp-admin\\css'
                nbr_folder_created += 1
            nbr2, size2, nbr_folder_created2, nbr_copied2, nbr_abs2, nbr_old2, size_copied2 = _sync(absf,absf2,bReverseOrder=bReverseOrder,bDryRun=bDryRun,bVerbose=bVerbose)
            nbr += nbr2
            size += size2
            nbr_folder_created += nbr_folder_created2
            nbr_copied += nbr_copied2
            nbr_abs += nbr_abs2
            nbr_old += nbr_old2
            size_copied += size_copied2
            continue
        nbr += 1
        bLongFile = 0
        if len(absf)>255:
            # cf https://stackoverflow.com/questions/36219317/pathname-too-long-to-open
            print("WRN: File src is long, converting to NT namming:\n'%s'" % absf)
            absf = "\\\\?\\" + absf.replace('/','\\')
            bLongFile = 1
        if len(absf2)>255:
            print("WRN: File dst is long, converting to NT namming:\n'%s'" % absf2)
            absf2 = "\\\\?\\" + absf2.replace('/','\\')
        sizeSrc = os.path.getsize(absf) # 1s pour 50000 fichiers sur 1 SD!
        size += sizeSrc
        bMustCopy = 0
        if not os.path.isfile(absf2):
            if bVerbose  and bVerboseFile: print("DBG: missing")
            nbr_abs += 1
            bMustCopy = 1
        elif sizeSrc != os.path.getsize(absf2):
            if bVerbose  and bVerboseFile: print("DBG: different size")
            nbr_old += 1
            bMustCopy = 1
        elif os.path.getmtime(absf) > os.path.getmtime(absf2):
            if bVerbose  and bVerboseFile: print("DBG: older")
            nbr_old += 1
            bMustCopy = 1
        if bMustCopy:
            try:
                if bDoIt: shutil.copyfile(absf,absf2)
                elif bVerbose and bVerboseFile: print("DRY: would create file '%s'" % absf2)
                nbr_copied += 1
                size_copied += sizeSrc
            except PermissionError as err:
                print("ERR: file copy permission error skipping: '%s'\n  err:%s" % (absf,err))
                handle(err)
            except OSError as err:
                print("ERR: file copy os error skipping: '%s'\n  err:%s" % (absf,err))
                handle(err)
        if bVerbose and 0: 
            print("DBG: sync: f: %s" % f )
            print("DBG: sync: bMustCopy: %s" % bMustCopy )
            print("DBG: sync: atime: %s" % os.path.getatime(absf) )
            print("DBG: sync: ctime: %s" % os.path.getctime(absf) )
            print("DBG: sync: mtime: %s" % os.path.getmtime(absf) )
            
            print("DBG: sync: atime: %s" % os.path.getatime(absf2) )
            print("DBG: sync: ctime: %s" % os.path.getctime(absf2) )
            print("DBG: sync: mtime: %s" % os.path.getmtime(absf2) )
            #~ break
            
    return nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied
            
def sync(src,dst,bReverseOrder=False,bDryRun=False,bVerbose=False):
    print("")
    strOptions = ""
    if bReverseOrder or bDryRun or bVerbose:
        strOptions += "[reverse:%s] " % bReverseOrder
        strOptions += "[dry run:%s] " % bDryRun
        strOptions += "[verbose:%s] " % bVerbose
    print("INF: %s => %s %s" % (src,dst,strOptions) )        
    if os.path.abspath(src) == os.path.abspath(dst):
        print("ERR: sync: can't copy a folder on itself")
        return
        
    time_begin = time.time()
    nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied = _sync( src, dst, bReverseOrder=bReverseOrder, bDryRun=bDryRun, bVerbose=bVerbose )
    print(" "*80) # clean preceding progression
    print("INF:     nbr total file: %s" % nbr )
    print("INF:     nbr total size: %sB (%s)" % (size,sizeToStr(size) ) )
    print("INF: nbr created folder: %s" % nbr_folder_created )
    print("INF:     file(s) copied: %s" % nbr_copied )
    print("INF:            missing: %s" % nbr_abs )
    print("INF:                old: %s" % nbr_old )
    print("INF:        size copied: %s" % size_copied )
    
    t = time.time()-time_begin
    bd = size_copied/t
    print("INF: in %5s [%s/s]" % (timeToString(t),sizeToStr(bd)) )
    
if __name__ == "__main__":
    #~ sync( "c:/tmp/test_rsync/", "c:/tmp/test_rsync_copy/")
    if len(sys.argv)<3:
        print("syntaxe: sync src dst [rev]\neg: sync c:\\ d:\\")
        exit(0)
        
    bReverseOrder = False
    bDryRun = False
    bVerbose = False
    if len(sys.argv)>3:
        for i in range(3,len(sys.argv)):
            if "dry" in sys.argv[i].lower():
                bDryRun = True
            if "inv" in sys.argv[i].lower() or "rev" in sys.argv[i].lower():
                bReverseOrder = True
            if "ver" in sys.argv[i].lower() or "rev" in sys.argv[i].lower():
                bVerbose = True
                
    sync(sys.argv[1], sys.argv[2],bReverseOrder=bReverseOrder,bDryRun=bDryRun, bVerbose=bVerbose)
    