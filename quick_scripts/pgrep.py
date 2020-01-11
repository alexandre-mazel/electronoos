# a grep clone in python
# I'm in a plane on windows, and no grep on my computer, let's develop one
import os
import sys
strElectroPath = "C:/Users/amazel/dev/git/electronoos/"
sys.path.append(strElectroPath+"/alex_pytools/")
#~ print sys.path
import stringmatch

def findInFile( filename, strToMatch ):
    """
    return the number of match
    """
    #~ print("INF:findInFile: searching in %s" % filename )
    strToMatchLower = strToMatch.lower()
    bFirstTime = True
    file = open(filename,"rt")
    nCptLine = 1
    nNbrMatch = 0
    while 1:
        line = file.readline()
        if line == None or len(line) == 0:
            break
        #~ print(l)
        if strToMatchLower in line.lower():
            if bFirstTime:
                bFirstTime = False
                print( "\n***** %s:" % filename )
                line=line.replace(chr(13),"")
            print( "%5d: %s" % (nCptLine,line) ), # , because each line already finished by a \n, so removing the print eol
            nNbrMatch += 1
        nCptLine += 1
    #~ print("%s: nbrLines: %d" % (filename,nCptLine))
    file.close()
    
    bBinary = True
    bBinary = False # the rb flash for open has no effect
    if bBinary:
        SEEK_SET = 0
        file = open(filename,"rb") # reopen as binary
        file.seek(0,SEEK_SET)
        buf = file.read()
        #~ if strToMatch in buf:  # search in binary is case sensitiv
        lenToMatch = len(strToMatch)
        for i in range(len(buf)-lenToMatch+1):
            if strToMatch == buf[i:i+lenToMatch]:
                print( "\n***** %s: (binary file, containing this string)" % filename )
                break

        file.close()
    return nNbrMatch


def findInFiles( strPath, strToMatch, mask = '*' ):
    """
    return nbr files analysed, nbr file where match is found and nbr total lines
    """
    aFiles = sorted(os.listdir(strPath))
    #~ print(aFiles)
    nbrLines = 0
    nbrFilesWithMatch = 0
    nbrFilesAnalysed = 0
    for strFile in aFiles:
        strFullPath = strPath + os.sep + strFile
        if os.path.isdir(strFullPath):
            #recursively check the folders
            na,nf,nl = findInFiles( strFullPath,strToMatch, mask)
            nbrFilesAnalysed += na
            nbrFilesWithMatch += nf
            nbrLines += nl
            continue
        if stringmatch.isMatch(strFile, mask):
            nl = findInFile(strFullPath,strToMatch)
            if nl > 0:
                nbrFilesWithMatch += 1
                nbrLines += nl
            nbrFilesAnalysed += 1
    return nbrFilesAnalysed,nbrFilesWithMatch,nbrLines
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print( "Grep clone\nsyntax: %s <string_to_match> <files_mask>\neg: %s my_string *.py" % ((sys.argv[0],)*2))
        exit(-1)
    print("\n")
    strToMatch,mask = sys.argv[1:3]
    na,nf,nl = findInFiles(".",strToMatch,mask.lower())
    print("Nbr Analysed Files: %d\nNbr Matching Files: %d\nNbr Total Line With Match: %d" % (na,nf,nl) )
            