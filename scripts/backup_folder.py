# -*- coding: cp1252 -*-

import os
import sys
import shutil
import time

"""
exemple: 

src hd:
8,15 Go (8 758 417 287 octets)
8,21 Go (8 826 269 696 octets) - sur disk
33 181 Fichiers, 1 Dossier

dst usb key:
8,15 Go (8 758 417 287 octets)
8,40 Go (9 029 025 792 octets)
33 181 Fichiers, 1 Dossiers

"""

def backupFolder( strSrc, strDst, nbrFilePerFolder = 10000 ):
    print("\nINF: backupFolder %s => %s\n                  max files per folder: %d\n" % (strSrc, strDst,nbrFilePerFolder) )
    
    if strDst[-1] == '/' or strDst[-1] == '\\':
        strDst = strDst[:-1]

    if strSrc[-1] != '/' and strSrc[-1] != '\\':
        strSrc += os.sep
        
    print("INF: backupFolder: sorting by alphabetic order...")
    listFiles = sorted(os.listdir(strSrc),reverse=False)
    print( "INF: backupFolder: source have %d file(s)" % len(listFiles) )
    
    nCptFile = 0
    nCptFolder = 0
    
    timeLastPrint = 0
    for f in listFiles:
        if (nCptFile % nbrFilePerFolder) == 0:
            nCptFolder += 1
            strDstFolderName = strDst + "_" + "%03d" % nCptFolder
            try:
                os.makedirs(strDstFolderName)
            except:
                print("\nWRN: backupFolder: folder %s already exists..." % strDstFolderName )
        if nCptFile > 33400 or 1: # permit to resume a previous copy, starting to a specific point (as file are sorted, they will be always in same order)
            shutil.copyfile(strSrc+f,strDstFolderName+os.sep+f)
        nCptFile += 1
        #~ if (nCptFile % 100) == 0 or time.time()-timeLastPrint > 1 or nCptFile==len(listFiles):
        if time.time()-timeLastPrint > 1. or nCptFile==len(listFiles):
            timeLastPrint = time.time()
            print("\rfolder: %d, copied: %d/%d" % (nCptFolder,nCptFile,len(listFiles)), end='')
    
    print("Done")
    
# backupFolder - end


if len(sys.argv)<3:
    print("Backup a folder with tons of file in many folder on another place")
    print("syntaxe: <script_name> src_folder dst_folder [nbr_max_file_per_folder default is 10,000]")
    print("eg: backup_folder.py c:\cvs\cvs_manual_divers\ E:\backup_obo\cvs_manual_divers")
    
    
src = sys.argv[1]
dst = sys.argv[2]
backupFolder(src,dst)