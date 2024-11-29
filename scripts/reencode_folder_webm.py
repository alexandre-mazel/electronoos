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
        strTemplateCommandLine = 'ffmpeg -y -i "%s" -c:a mp3 "%s"' # y to overwrite when previous file was 0 sized
        strDstExt = "mp3"
    else:
        strTemplateCommandLine = 'ffmpeg -y -i "%s" -c:a libvorbis -q 5 "%s"'
        strDstExt = "ogg"

    path = os.path.dirname(srcFilename)
    basename = os.path.basename(srcFilename)    
    filenoext,ext = os.path.splitext(basename)

    dst = filenoext + "." + strDstExt
    dst  = cleanString( dst )
    dst = dst.replace(" ", "_").replace(":", "_").replace("!", "_").replace("?", "_").replace("*", "_")
    absdst = path + os.sep + dst
    if not os.path.isfile(absdst) or os.stat(absdst).st_size == 0:
        print("INF: Creating: '%s'" % absdst )
        strCommandLine = strTemplateCommandLine % (srcFilename, absdst)
        os.system(strCommandLine)
        # todo: remplir le tag id3
    else:
        print("INF: Already existing: '%s'" % dst )
        
        
        
        

def encodeFolder(strPath):
    print("INF: encodeFolder: encoding '%s'" % strPath )
    listFiles = sorted(os.listdir(strPath))
    for f in listFiles:
        reencode(strPath + f )
    print("INF: encodeFolder: done"  )
    
    
    
s = "d:/webm/"
encodeFolder(s)
    
    