# a grep clone in python
# I'm in a plane on windows, and no grep on my computer, let's develop one
import os
import sys

def findInFile( filename, strToMatch ):
    #~ print("INF:findInFile: searching in %s" % filename )
    bFirstTime = True
    file = open(filename,"rt")
    nCptLine = 1
    while 1:
        line = file.readline()
        if line == None or len(line) == 0:
            break
        #~ print(l)
        if strToMatch in line.lower():
            if bFirstTime:
                bFirstTime = False
                print( "\n***** %s:" % filename )
                line=line.replace(chr(13),"")
            print( "%5d: %s" % (nCptLine,line) ), # , because each line already finished by a \n, so removing the print eol
        nCptLine += 1
    file.close()


def findInFiles( strPath, strToMatch, mask ):
    aFiles = sorted(os.listdir(strPath))
    #~ print(aFiles)
    for strFile in aFiles:
        strFullPath = strPath + os.sep + strFile
        if os.path.isdir(strFullPath):
            #recursively check the folders
            findInFiles( strFullPath,strToMatch, mask)
            continue
        if mask in strFile or 1: # masking doesn't match right now!
            findInFile(strFullPath,strToMatch)
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print( "Grep clone\nsyntax: %s <string_to_match> <files_mask>\neg: %s my_string *.py" % (sys.argv[0])*2)
        exit(-1)
    strToMatch,mask = sys.argv[1:3]
    findInFiles(".",strToMatch,mask.lower())
            