import sys

def pause():
    import msvcrt
    import time
    while not msvcrt.kbhit():
        time.sleep(0.1)
    msvcrt.getch()


def findSpecificChar(filename, nSpecificValue, nReplaceByValue = None ):
    """
    find a specific code value in a file
    - specific_code: eg 0xA0
    """
    out = "" # create a new string if nReplaceByValue is set
    print( "INF: Looking for %d (0x%x) in file '%s'" % ( nSpecificValue, nSpecificValue, filename ) )
    
    nbr_found = 0
        
    if nReplaceByValue != None: 
        print( "WRN: Will patch with value %d (0x%x)" % (nReplaceByValue,nReplaceByValue) )
    with open( filename, "r", encoding="utf-8" ) as f:
        for lineno, line in enumerate(f, 1):
            for col, c in enumerate(line):
                if ord(c) == nSpecificValue:
                    print(f"char {nSpecificValue} at Line {lineno}, col {col} (char before: %s)" % (line[max(0,col-16):col]) )
                    nbr_found += 1
                    
                    if nReplaceByValue != None:
                        out += chr(nReplaceByValue)
                    
                elif nReplaceByValue != None: 
                    out += c
                    
            #~ if nReplaceByValue != None: # already done as the last char of each line is already a "\n"
                #~ out += "\n"
                    
    
    print( "INF: Found char(s): %d" % nbr_found )
    
    if nReplaceByValue != None and nbr_found > 0:
        # save
        print( "\nWRN: About to save patched file, changing %d char(s) with char code %d (0x%x, char: '%s')" % (nbr_found, nReplaceByValue,nReplaceByValue,chr(nReplaceByValue)) )
        print( "Press a key to proceed ot Ctrl+C to abort ..." )
        pause()
        f = open( filename, "w", encoding="utf-8" )
        f.write(out)
        f.close()
        
                
# findNonAscii - end


if __name__ == "__main__":
    
    if len(sys.argv)< 2:
        print("Find a specific char in a utf-8 encoded file (eg a python source)")
        print("syntaxe: scriptname <filename_to_search_into> <value in decimal> or x<value in hexadecimal> [replace_char]")
        print("         eg: scriptname file.py xA0 ")
        exit(0)
        
    fn = sys.argv[1]
    
    nSpecificValue = None
    nDestValue = None
    if len(sys.argv)>2:
        p = sys.argv[2]
        if 'x' in p:
            nSpecificValue = int(p[1:],16)
        else:
            nSpecificValue = int(p)
    
    nReplaceByValue = None
    if len(sys.argv)>3:
        p = sys.argv[3]
        if 'x' in p:
            nReplaceByValue = int(p[1:],16)
        else:
            nReplaceByValue = int(p)
    
    #~ findNonAscii(fn, bOnlyNotFrench = True)
    findSpecificChar(fn, nSpecificValue = nSpecificValue, nReplaceByValue=nReplaceByValue)
    #~ testFileEncoding(fn)
    
print("\nFinished...")