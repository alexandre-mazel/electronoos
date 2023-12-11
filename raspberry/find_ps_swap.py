import os

def findInfoInFile(filename,word, listExcludeString = []):
    """
    output all line containing word
    """
    word = word.lower()
    out = ""
    f = open(filename,"r")
    while 1:
        line = f.readline()
        if len(line)<1:
            break
        if word in line.lower():
            #~ print("hit on word: '%s'" % word)
            if len(listExcludeString)>0:
                for ex in listExcludeString:
                    if ex.lower() in line.lower():
                        #~ print("hit ex")
                        break
                else:
                    # ex not found
                    out += line
            else:
                # nothing in listExclude
                out += line
    f.close()
    return out
            

def findProcessWithSwap():
    strPath = "/proc/"
    aFiles = sorted(os.listdir(strPath))
    for f in aFiles:
        if not f.isdigit():
            continue
        filename = strPath+f + "/status"
        s = findInfoInFile(filename,"swap",["0 kB","Name"])
        if len(s)>0:
            name = findInfoInFile(filename,"Name").replace("\n","").replace("\t" ,"").replace( "  ", " ")
            print("%s: %s: %s" % (f, name, s), end="" ) # a lancer en python3
        
findProcessWithSwap()