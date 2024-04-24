import sys

def pause():
    import msvcrt
    import time
    while not msvcrt.kbhit():
        time.sleep(0.1)
    msvcrt.getch()


def findNonAscii(filename, bOnlyNotFrench = False, nSpecificValue = None):
    """
    find all non ascii accent in a text
    - bOnlyNotFrench: only non french accent
    - nSpecificValue: specify a value (if set, it overwrite bOnlyNotFrench)
    """
    #~ listKnownFrenchAccent = [0xE0, 0xE8, 0xE9]
    f = open(filename,"rb")
    buf = f.read()
    print( "INF: findNonAscii in file '%s' of size: %d" % (filename, len(buf)))
    i = 0
    nCountBeforePause = 0
    if nSpecificValue != None:
        bOnlyNotFrench = False
        
    while i < len(buf):
        n = buf[i]
        if (not bOnlyNotFrench and n > 127 and (nSpecificValue == None or n == nSpecificValue) ) \
            or (bOnlyNotFrench and n > 127 and (n < 0xC0 or n > 0xF6 ) ) \
            :
            print("at %d: char: %d (0x%02X), txt prec: '%s'" % (i, n, n,buf[i-30:i]) )
            nCountBeforePause += 1
            if nCountBeforePause > 24:
                nCountBeforePause = 0
                print("pause...")
                pause()
        i += 1
        
        
    f.close()
# findNonAscii - end
    


if __name__ == "__main__":
    if len(sys.argv)< 2:
        print("syntaxe: filename to search into")
        exit(0)
    fn = sys.argv[1]
    
    nSpecificValue = None
    if len(sys.argv)>2:
        p = sys.argv[2]
        if 'x' in p:
            nSpecificValue = int(p,16)
        else:
            nSpecificValue = int(p)
    
    #~ findNonAscii(fn, bOnlyNotFrench = True)
    findNonAscii(fn, nSpecificValue = nSpecificValue)