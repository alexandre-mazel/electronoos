import os
import sys

def showOffset( filename, nOffset ):
    """
    print a portion of a file around an offset 
    """
    nSurrounding = 40
    nLenFile = os.path.getsize( filename )
    print( "INF: showOffset in file '%s' of size: %d at offset: %s" % (filename, nLenFile, nOffset))
    f = open(filename,"rb")

    f.seek(max(0,nOffset-nSurrounding))
    buf = f.read(nSurrounding)
    print("Before %d: %s" % (nOffset,buf) )
    
    buf = f.read(nSurrounding)
    print("After %d: %s" % (nOffset,buf) )
        
    f.close()
    
# showOffset - end
    

def testFileEncoding( filename ):
    print("INF: testFileEncoding: testing file '%s'..." % filename )
    try:
        f = open(filename,"rt", encoding='cp1252')
        buf = f.read()
        f.close()
    except UnicodeDecodeError as err:
        print("ERR: %s" % err )
        showOffset(filename,err.start)
        return
    print("")
    print("GOOD: this file has a correct encoding!")


if __name__ == "__main__":
    
    if len(sys.argv)< 2:
        print("Show character at an offset of a file")
        print("syntaxe: scriptname <filename_with_contents> <offset (default: 0) - if no offset, test file encoding>")
        exit(0)
        
    fn = sys.argv[1]
    
    nOffset = -1
    if len(sys.argv)>2:
        p = sys.argv[2]
        if 'x' in p:
            nOffset = int(p,16)
        else:
            nOffset = int(p)
            
    print()
    if nOffset != -1:
        showOffset(fn, nOffset = nOffset)
    else:
        testFileEncoding(fn)