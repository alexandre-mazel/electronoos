import os

def findInfoInFile(filename,word):
    """
    output all line containing word
    """
    s = ""
    f = open(filename,"r")
    while 1:
        line = f.readline()
        if word in line.lower():
            s += line
    return s
            

def findProcessWithSwap():
    strPath = "/proc/"
    aFiles = sorted(os.listdir(strPath))
    for f in aFiles:
        if not isdigit(f):
            continue
        s = findInfoInFile(strPath+f,"swap")
        print("%s: %s" % f, s)
        
        
findProcessWithSwap()