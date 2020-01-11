def assert_check( value, reference = True ):
    print( "assert_check: %s ? %s" % (value, reference) )
    if( value != reference ):
        print( "ERR: assert_check: '%s' != '%s'" % (value, reference) )
        assert(0)    
        
def isMatch( s, ref ):
    return isMatchFill(s,ref)[0]
    
def isMatchFill( s, ref ):
    """
    is s match the ref.
    - s: a string
    - ref: a string to match, eg: "*toto*", "*.py", "je m'appelle *".
      with '*': 0 or n char
    Return a pair: [bool, dict] with bool: True if it match and dict, a dict with filled wildcard, eg "$1": "Alexandre"
    """
    dOut = {}
    js = 0 # because "is" is a keyword
    jref = 0
    numCurWild = 0
    bInStar = False
    bMatch = False
    while 1:
        if len(s) == js:
            if len(ref) == jref:
                bMatch = True
            else:
                bMatch = False
            break
        if len(ref) == jref:
            assert(0)
                
        if not bInStar:
            if ref[jref] == '*':
                bInStar = True
                sEatStar = ""
        if not bInStar:
            if s[js] != ref[jref]:
                bMatch = False
                break
        else:
            sEatStar += s[js]
        js += 1
        if not bInStar:
            jref += 1
           
    print("DBG: isMatchFill: %s and %s => (%s,%s)" % (s,ref,bMatch,dOut) )
    return bMatch, dOut
# isMatchFill - end
    
    
        
        
        
        
        
        
def autoTest():
    assert_check( isMatch( "", "" ) )
    assert_check( isMatch( "tu", "tu" ) )
    assert_check( isMatch( "tu", "ta" ), False )
    assert_check( isMatch( "tu", "tua" ), False )
    assert_check( isMatch( "tu", "tu*" ) )
    assert_check( isMatch( "toto.py", "*.py" ) )
    assert_check( isMatch( "toto.pa.py", "*.py" ) )
    assert_check( isMatch( "toto.pya", "*.py" ), False )
    assert_check( isMatch( "toto.pya", "*.py*" ), False )
    assert_check( isMatchFill( "toto.pya", "*.py*" ), (True, {"$1":"toto", "$2":"a"} ) )
    assert_check( isMatchFill( "Je m'appelle coco et je suis content.", "*appelle * *" ), (True, {"$1":"Je m'", "$2":"coco", "$3": "et je suis content."} ) )
        
        
        
        
if __name__ == "__main__":
    autoTest();