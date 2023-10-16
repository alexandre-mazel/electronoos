import os
import sys


def androidRessourceNormalise(strPath):
    """
    rename all file in path to match only lower case and _
    """
    print("INF: androidRessourceNormalise: working on '%s'" % strPath )
    
    nNbrRenammed = nNbrTotalFile = 0
    listFiles = os.listdir(strPath)
    for f in listFiles:
        absf = strPath + os.sep + f
        if not os.path.isfile(absf):
            continue
        new = f.lower()
        new = new.replace(" ", "_").replace("-","_")
        nNbrTotalFile += 1
        if new != f:
            absnew = strPath + os.sep + new
            print("INF: androidRessourceNormalise: '%s' => '%s'" % (f,new))
            os.rename(absf,new)
            nNbrRenammed += 1
            
    print( "INF: %d file(s) on a %d file(s)" % (nNbrRenammed, nNbrTotalFile))
    
    
strPath = "."
if len(sys.argv)>1:
    strPath = sys.argv[1]
androidRessourceNormalise(strPath)