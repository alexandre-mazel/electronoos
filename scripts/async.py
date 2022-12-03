import os
import shutil
import sys
import time

sys.path.append( "../alex_pytools/")
from stringtools import timeToStr, sizeToStr

def isDirMark(c):
    return c == '/' or c == '\\'
    
def get_last_folder(path):
    """
    c:/toto/tutu/ => tutu
    """
    idx1 = path[:-1].find('/')
    idx2 = path[:-1].find('\\')
    return path[max(idx1,idx2):].replace('/','').replace('\\','')

def _sync(src,dst):
    """
    synchronise 2 folders: 
      make sure all in src will be copied in dst, 
      but extra file in dst won't be erased.
      So renaming one file in src will leave original name in dst
    
    Retourne le nbr de fichier dans la src, la taille totale, le nbr de dossier cree, nbr de fichier copie dans dst, (le nombre qui etait absent et le nombre qui devait etre mis a jour)
    - src et dst doivent finir par un os.sep
    """
    bVerbose = 1
    bVerbose = 0
    if not isDirMark(src[-1]): src += os.sep
    if not isDirMark(dst[-1]): dst += os.sep
        
    nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied = 0,0,0,0,0,0,0
    
    if not os.path.isdir(dst):
        if bVerbose: print("DBG: sync: creating %s" % dst)
        os.mkdir(dst)
        nbr_folder_created += 1
        
    last_folder = get_last_folder(src)
    if bVerbose: print("DBG: sync: last_folder:'%s'\n\n" % last_folder)
    if last_folder == "$RECYCLE.BIN":
        print("WRN: skipping: '%s'" % src)
        return nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied        
    
    try:
        listSrc = os.listdir(src)
    except PermissionError as err:
        print("WRN: access error skipping folder    : '%s'" % src)
        return nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied
    listSrc = sorted(listSrc)
    for f in listSrc:
        if (nbr & 47)==0: # un nombre premier sympa
            out_src = src
            if len(out_src)>40:
                out_src = "..." + out_src[-40:]
            print('processed files: %s: %9d(%d)'%(out_src,nbr,nbr_copied) + " "*20, end="\r")
        absf = src + f
        absf2 = dst + f
        if os.path.isdir(absf):
            if not os.path.isdir(absf2):
                if bVerbose: print("DBG: sync: creating %s" % absf2)
                os.mkdir(absf2)
                nbr_folder_created += 1
            nbr2, size2, nbr_folder_created2, nbr_copied2, nbr_abs2, nbr_old2, size_copied2 = _sync(absf,absf2)
            nbr += nbr2
            size += size2
            nbr_folder_created += nbr_folder_created2
            nbr_copied += nbr_copied2
            nbr_abs += nbr_abs2
            nbr_old += nbr_old2
            size_copied += size_copied2
            continue
        nbr += 1
        sizeSrc = os.path.getsize(absf)
        size += sizeSrc
        bMustCopy = 0
        if not os.path.isfile(absf2):
            if bVerbose: print("DBG: missing")
            nbr_abs += 1
            bMustCopy = 1
        elif sizeSrc != os.path.getsize(absf2):
            if bVerbose: print("DBG: different size")
            nbr_old += 1
            bMustCopy = 1
        elif os.path.getmtime(absf) > os.path.getmtime(absf2):
            if bVerbose: print("DBG: older")
            nbr_old += 1
            bMustCopy = 1
        if bMustCopy:
            try:
                shutil.copyfile(absf,absf2)
                nbr_copied += 1
                size_copied += sizeSrc
            except PermissionError as err:
                print("WRN: file copy permission error skipping: '%s'" % absf)
            except OSError as err:
                print("WRN: file copy os error skipping: '%s'" % absf)
        if bVerbose: 
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
            
def sync(src,dst):
    print("")
    print("INF: %s => %s" % (src,dst) )        
    if os.path.abspath(src) == os.path.abspath(dst):
        print("ERR: sync: can't copy a folder on itself")
        return
        
    time_begin = time.time()
    nbr, size, nbr_folder_created, nbr_copied, nbr_abs, nbr_old, size_copied = _sync( src, dst )
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
    print("INF: in %5s [%s/s]" % (timeToStr(t),sizeToStr(bd)) )
    
if __name__ == "__main__":
    #~ sync( "c:/tmp/test_rsync/", "c:/tmp/test_rsync_copy/")
    if len(sys.argv)<3:
        print("syntaxe: sync src dst\neg: sync c:\\ d:\\")
        exit(0)
    sync(sys.argv[1], sys.argv[2])
    