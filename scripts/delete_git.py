"""
Erase all .git from a folder and subfolder
"""
import os
import shutil

def eraseAllGit(strPath = "./"):
    #~ print("INF: scanning '%s'" % strPath )
    nNbrDeletedFolder = 0
    if strPath[-1] != '/':
        strPath += '/'
    li = os.listdir(strPath)
    for f in li:
        absf = strPath + f
        if os.path.isdir(absf):
            if f == ".git":
                todel = absf.replace('/',os.sep)
                print("INF: erasing '%s'" % todel)
                #~ os.unlink(todel)
                #~ shutil.rmtree(todel) # permission error
                os.system( "del /s /q /f " + todel)
                shutil.rmtree(todel) # efface le dossier vide
                nNbrDeletedFolder += 1
            else:
                nNbrDeletedFolder += eraseAllGit(absf)
    return nNbrDeletedFolder
# eraseAllGit - end



if __name__ == "__main__":
    print("WRN: it will erase all .git subfolder from current folder !")
    print("- press enter to continue -")
    input()
    n = eraseAllGit()
    print("INF: nNbrDeletedFolder: %d" % n )