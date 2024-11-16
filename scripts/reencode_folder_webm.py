import os

import sys
sys.path.append("../statis3")
from statis3 import replaceNameReplaceByNonAccentuatedChars

def cleanString(s):
    s = s.encode("ascii", errors="namereplace").decode("ascii")
    s = s.replace( " * ", " - " ) # for unsaved document in scite
    s = replaceNameReplaceByNonAccentuatedChars(s)
    return s

def reencode(srcFilename):
    bMp3 = False
    bMp3 = True
    
    
    if bMp3:
        strTemplateCommandLine = 'ffmpeg -i "%s" -c:a mp3 "%s"'
        strDstExt = "mp3"
    else:
        strTemplateCommandLine = 'ffmpeg -i "%s" -c:a libvorbis -q 5 "%s"'
        strDstExt = "ogg"

    path = os.path.dirname(srcFilename)
    basename = os.path.basename(srcFilename)    
    filenoext,ext = os.path.splitext(basename)

    dst = filenoext + "." + strDstExt
    dst  = cleanString( dst )
    dst = dst.replace(" ", "_").replace(":", "_").replace("!", "_").replace("?", "_").replace("*", "_")
    dst = path + os.sep + dst
    if not os.path.isfile(dst):
        print("INF: Creating: '%s'" % dst )
        strCommandLine = strTemplateCommandLine % (srcFilename, dst)
        os.system(strCommandLine)
        # todo: remplir le tag id3
        
        
        

def encodeFolder(strPath):
    listFiles = sorted(os.listdir(strPath))
    for f in listFiles:
        reencode(strPath + f )
    
    
    
s = "d:/webm/"
encodeFolder(s)
    
    