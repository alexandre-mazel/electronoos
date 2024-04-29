# -*- coding: cp1252 -*-

# a grep clone in python
# I'm in a plane on windows, and no grep on my computer, let's develop one
import os
import sys
strElectroPath = "C:/Users/alexa/dev/git/electronoos/"
sys.path.append(strElectroPath+"/alex_pytools/")
#~ print sys.path
import misctools
import stringmatch

def findInFile( filename, strToMatch, bVerbose = True ):
    """
    return the number of analysed line,number of match
    """
    if bVerbose: print("\nINF:findInFile: searching in %s" % filename )
    strToMatchLower = strToMatch.lower()
    bFirstTime = True
    file = open(filename,"rt")
    nCptLine = 1
    nNbrMatch = 0
    nNbrErrorDecode = 0
    nCptLineAnalysed = 0
    while 1:
        try:
            line = file.readline() # ATTENTION READLINE A UNE LIMITE SUR LES GROS FICHIERS: il ne retourne pas toutes les lignes.
            #~ print("DBG: nCptLine: %d, offset: %s" % (nCptLine,file.tell() ) )
            if line == None or len(line) == 0:
                break
        except UnicodeDecodeError as err:
            if bVerbose or 0: print( "WRN: decode error: %s\n=> skipping line %d in '%s'" % (str(err),nCptLine, filename) )
            nCptLine += 1
            nNbrErrorDecode += 1
            if nNbrErrorDecode > 3:
                if bVerbose: print( "WRN: two much decode error, skipping '%s'\n" % filename )
                return nCptLineAnalysed,nNbrMatch
            continue
            
        nCptLineAnalysed += 1
            
        #~ print(l)
        # try with a double test
        #if stringmatch.isMatch(line.lower(),strToMatchLower): # will force to enclose the word to look for between * (boring)
        # if strToMatchLower in line.lower(): # work with singe word, but not with two word separated by a *
        if bVerbose: print("DBG: findInFile: looking for '%s' in '%s'" % (strToMatchLower,line))
        if strToMatchLower in line.lower() or stringmatch.isMatch(line.lower(),strToMatchLower):
            if bFirstTime:
                bFirstTime = False
                stamp = misctools.getTimeStamp()
                print( "\n***** %s (date: %s):" % (filename,stamp) )
                line=line.replace(chr(13),"")
            lenLineMax = 200
            if len(line)>lenLineMax:
                line = line[:lenLineMax-3]+ "..."
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
    return nCptLineAnalysed,nNbrMatch


def findInFiles( strPath, strToMatch, strFileMask = '*', bVerbose = True, bShowResultInTextEditor = False, bInternalCall = False ):
    """
    return nbr files analysed, nbr file where match is found and nbr total lines
    """
    try:
        aFiles = sorted(os.listdir(strPath))
    except PermissionError as err:
        print("WRN: findInFiles: permission error for '%s'" % strPath)
        return 0,0,0,0
    #~ print(aFiles)

    nbrFilesAnalysed = 0
    nbrFilesWithMatch = 0
    nbrLinesAnalysed = 0
    nbrLinesWithMatch = 0
    
    listFilesToView = []
    
    for strFile in aFiles:
        strFullPath = strPath + os.sep + strFile
        if os.path.isdir(strFullPath):
            #recursively check the folders
            na,nf,nla,nlm, listFiles = findInFiles( strFullPath,strToMatch, strFileMask,bVerbose=bVerbose,bShowResultInTextEditor=bShowResultInTextEditor,bInternalCall=True)
            if bShowResultInTextEditor: listFilesToView.extend(listFiles)
            nbrFilesAnalysed += na
            nbrFilesWithMatch += nf
            nbrLinesAnalysed += nla
            nbrLinesWithMatch += nlm
            continue
        if 0:
            if ".exe" in strFile or ".dll" in strFile:
                if bVerbose: print("WRN: skipping binary style file: '%s'" % strFile)
                continue
        bMatch = stringmatch.isMatch(strFile.lower(), strFileMask)
        if "ous" in strFile and 0: print("DBG: match: '%s' / '%s' => %s" % (strFile, strFileMask,bMatch) )
        if bMatch:
            nla,nlm = findInFile(strFullPath,strToMatch,bVerbose=bVerbose)
            if nlm > 0:
                nbrFilesWithMatch += 1
                if bShowResultInTextEditor: listFilesToView.append(strFullPath)
            nbrLinesAnalysed += nla
            nbrLinesWithMatch += nlm
            nbrFilesAnalysed += 1
            
    if not bInternalCall  and bShowResultInTextEditor and len(listFilesToView)>0:
        print("INF: opening %s file(s) in text editor..." % len(listFilesToView) )
        strCommandLine = "scite "
        for f in listFilesToView:
            strCommandLine += '"%s" ' % f
        #~ print("command: '%s'" % strCommandLine)
        os.system(strCommandLine)
        
    return nbrFilesAnalysed,nbrFilesWithMatch,nbrLinesAnalysed,nbrLinesWithMatch,listFilesToView
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print( "\n  My Grep-clone v1.0\n\n  syntax: %s <string_to_match> <files_mask> [1] [show]\n\n  eg: %s a_word_in_a_line *.py\n  eg: %s *word1*word2* face*\n  eg: %s any_string_with_some* * 1 => will print binary file skipped file(s)\n      if option show: open all hitting file(s) in scite" % ((sys.argv[0],)*4))
        exit(-1)
    print("\n")
    
    bShowResultInTextEditor = False
    
    bVerbose = 0
    if len(sys.argv)>3 and sys.argv[3]=='1':
        bVerbose = 1
    #strToMatch,mask = sys.argv[1:3]
    if len(sys.argv)>1:
        strToMatch = sys.argv[1]
    if len(sys.argv)>2:
        mask = sys.argv[2]
    else:
        mask = "*.*"
        
    if len(sys.argv)>3:
        if sys.argv[3]:
            bShowResultInTextEditor = 1
        
    print("INF: bVerbose: %s" % bVerbose ) 
    na,nf,nla,nlm,listfiles = findInFiles(".",strToMatch,mask.lower(),bVerbose=bVerbose,bShowResultInTextEditor=bShowResultInTextEditor)
    print("\nNbr Analysed Files: %d\nNbr Matching Files: %d\nNbr Total Line Analysed: %d\nNbr Total Line With Match: %d" % (na,nf,nla,nlm) )
            