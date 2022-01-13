#!/usr/bin/env python3
"""
Launch a scite text editor with all modified file in the local git repository 
"""

import os

def getModifiedFileLists():
    """
    list all files modified in the current git
    """
    strFileTmp = "/tmp/diff_file.tmp"
    os.system("git status --porcelain -uno>" + strFileTmp)
    f = open(strFileTmp,"rt")
    listModified = []
    while 1:
        s = f.readline()
        s = s.replace("\n","")
        if len(s)<1:
            break
        if s[:2] == " M":
            strFile= s[3:]
            print("INF: getModifiedFileLists: file '%s'" % strFile )
            listModified.append(strFile)
    return listModified

def editListFile( listFiles ):
    if len(listFiles) < 1:
        print("WRN: No file to edit")
    
    strFiles = " ".join(listFiles)
    os.system( "scite %s &" % strFiles )
    
    
li = getModifiedFileLists()
editListFile( li )