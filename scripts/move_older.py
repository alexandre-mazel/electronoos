import os
import sys
import time

sys.path.append( os.path.dirname(__file__) + "/../alex_pytools/" )
import misctools


def move_older( strPath = "", strBackupPath = "moved_files", nOlderThanMin = 10 ):
    """
    move file older than 10 min to another folder
    - strBackupPath: place to move files
    """
    bVerbose = 1
    bVerbose = 0
    
    if strPath[-1] != os.sep: strPath += os.sep
        
    print("INF: move_older: strPath: '%s'" % strPath )
    
    listFiles = os.listdir(strPath)
    # start with older
    listFiles = sorted(listFiles, key=lambda x: os.path.getmtime(strPath+x),reverse=False)
    
    for f in listFiles:
        body,ext = os.path.splitext(f)
        #~ if ext not in [".pdf", ".doc", ".docx", ".jpg"]:
            #~ continue
            
        absf = strPath + f
        if not os.path.isfile(absf):
            continue
            
        modtime = os.path.getmtime(absf)
        age = time.time() - modtime
        #~ print(age)
        if age < 60*nOlderThanMin:
            # this file was modified less than 1 min
            print("INF: move_older: Next older file is %.1f min" % (age/60) )
            break
            
        print("INF: move_older: moving age %.1fs: %s" % (age,ascii(f)))
        dst = strPath + os.sep + strBackupPath + os.sep
        try: os.makedirs(dst)
        except FileExistsError as err: pass
        try: 
            os.rename(absf,dst+f)
        except FileExistsError as err: 
            cpt = 1
            body,ext = os.path.splitext(f)
            while os.path.isfile(dst+body+("__%04d"%cpt)+ext):
                cpt += 1
                
# move_older - end
    
move_older(sys.argv[1])
print("done")