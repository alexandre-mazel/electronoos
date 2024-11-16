import sys
sys.path.append("../alex_pytools/")
sys.path.append("C:/Users/alexa/dev/git/electronoos/alex_pytools/")
import misctools
import time

def del_duplicate( strPath, bReallyDelete ):
    print("INF: del_duplicate: bReallyDelete: %s, strPath: %s" % (bReallyDelete,strPath) )

    listDup = misctools.findDuplicate(strPath)
    #~ print("
    if len(listDup)>0 and bReallyDelete:
        print("\nWRN: will erase %s file(s) in 4 sec...\n" % len(listDup))
        time.sleep(4) # time for user to kill
        misctools.eraseFiles(listDup, strPath)
            
            


if __name__ == "__main__":
    
    if len(sys.argv)< 2:
        print("Delete all duplicate file in a folder")
        print("syntaxe: scriptname <folder> [del]")
        print("     eg: scriptname . del")
        print("         del: really delete")
        exit(0)
        
    path = sys.argv[1]
    
    bReallyDelete = False
    if len(sys.argv) > 2:
        bReallyDelete = sys.argv[2][:3].lower() == "del"
    
    del_duplicate( path, bReallyDelete )