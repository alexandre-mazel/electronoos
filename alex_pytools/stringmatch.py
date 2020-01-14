global_nCountAssert = 0
def assert_check( value, reference = True ):
    global global_nCountAssert
    global_nCountAssert += 1
    print( "%d: assert_check: %s  ?  %s" % (global_nCountAssert,value, reference) )
    if( value != reference ):
        print( "ERR: assert_check: '%s' != '%s'" % (value, reference) )
        assert(0)    
        
def isMatch( s, ref ):
    return isMatchFill(s,ref)[0]
    
def getFirstWord( s ):
    """
    return the first  word in s
    return "" if word start with a space or ...
    """
    sep = " .,;:?!"
    for i,c in enumerate(s):
        if c in sep:
            break
    else:
        return s
    return s[:i]
    
    
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
    numCurWild = 1
    bInStar = False
    bMatch = False
    sEatStar = ""
    while 1:
        if len(s) == js:
            if len(ref) == jref:
                bMatch = True
                break
            if ref[jref] == '*' and len(ref)==jref+1: # * was the last char
                # if not bInStar, sEatStar is ""
                dOut["$"+str(numCurWild)] = sEatStar
                bMatch = True
            else:
                #~ print("DBG: arrived at end of s and not ref: '%s'"% ref)
                bMatch = False
            break
            
        if len(ref) == jref:
            #~ print("DBG: arrived at end of ref: '%s'"% ref)
            bMatch = False
            break
                
        if not bInStar:
            if ref[jref] == '*':
                bInStar = True
                sEatStar = ""
                if len(ref) != jref+1 and ref[jref+1] == '*':
                    # specific case to correct bug of the "**"
                    jref += 1
                    dOut["$"+str(numCurWild)] = ""
                    numCurWild += 1
                
        if not bInStar:
            if s[js] != ref[jref]:
                #~ print("DBG: no match of current char: remaining '%s' and '%s'"% (s[js:],ref[jref:]))
                bMatch = False
                break
        else:
            if not isMatch( s[js:], ref[jref+1:] ): # and (len(ref) == jref+1 or ref[jref+1] != '*'):
                # so it remains to eat
                sEatStar += s[js]
            else:
                dOut["$"+str(numCurWild)] = sEatStar
                numCurWild += 1
                bInStar = False
                jref += 1
            
            
        js += 1
        if not bInStar:
            jref += 1
           
    print("DBG: isMatchFill: '%s' and '%s' => (%s,%s)" % (s,ref,bMatch,dOut) )
    return bMatch, dOut
# isMatchFill - end

def isMatchFillVar( s, ref ):
    """
    same as isMatchFill, but ref can mix some * and some $variable_name
    - variable_name is a string without spaces
    eg: "je m'appelle alexandre", "*appelle $name"
    
    """
    jref = 0
    dIdx = {} # index => var name
    nNumIdx = 1
    newref = ""
    while jref < len(ref):
        if ref[jref] == '$':
            w = getFirstWord( ref[jref+1:] )
            dIdx["$"+str(nNumIdx)] = w
            jref += len(w)
            newref += "*"
            nNumIdx += 1
        elif ref[jref] == '*':
            nNumIdx += 1
            newref += "*"
        else:
            newref += ref[jref]
        jref += 1
        
    print("DBG: isMatchFillVar: dIdx:%s" % dIdx )
    retVal = isMatchFill( s, newref )
    if not retVal[0]:
        return retVal
        
    dNew = {}
    nNumStar = 1
    for k,v in sorted(retVal[1].items()):
        if k in dIdx:
            dNew[dIdx[k]] = v
        else:
            dNew["$"+str(nNumStar)] = v
            nNumStar += 1
    return retVal[0], dNew
# isMatchFillVar - end
    
    
    
        
        
        
        
        
        
def autoTest():
    assert_check( getFirstWord("toto est la" ), "toto" )
    assert_check( getFirstWord("tota," ), "tota" )
    assert_check( getFirstWord("tutu" ), "tutu" )
    assert_check( getFirstWord("t" ), "t" )
    assert_check( getFirstWord("," ), "" )
    assert_check( getFirstWord("" ), "" )
    assert_check( isMatch( "", "" ) )
    assert_check( isMatch( "tu", "tu" ) )
    assert_check( isMatch( "tu", "ta" ), False )
    assert_check( isMatch( "tu", "tua" ), False )
    assert_check( isMatchFill( "tu", "tu*" ), (True, {"$1":""} )  )
    assert_check( isMatchFill( "toto.py", "*.py" ), (True, {"$1":"toto"} )  )
    assert_check( isMatch( "toto.pa.py", "*.py" ) )
    assert_check( isMatch( "toto.pya", "*.py" ), False )
    assert_check( isMatch( "toto.pya", "*.py*" ), True )
    assert_check( isMatchFill( "toto.pya", "*.py*" ), (True, {"$1":"toto", "$2":"a"} ) )
    assert_check( isMatchFill( "Je m'appelle Alexandre et je suis content.", "*appelle * *" ), (True, {"$1":"Je m'", "$2":"Alexandre", "$3": "et je suis content."} ) )
    
    # le suivant est un peu tordu, le resultat attendu pourrait etre:
    # $2 = , $3=Alexandre et je suis content.
    # ou
    # $2 = Alexandre et je suis content., $3=
    # couramment on a ca (bug of the "**") => patched
    # $2 = A, $3=lexandre et je suis content.
    #assert_check( isMatchFill( "Je m'appelle Alexandre et je suis content.", "*appelle **" ), (True, {"$1":"Je m'", "$2":"A", "$3": "lexandre et je suis content."} ) )
    assert_check( isMatchFill( "Je m'appelle Alexandre et je suis content.", "*appelle **" ), (True, {"$1":"Je m'", "$2":"", "$3": "Alexandre et je suis content."} ) )
        
    assert_check( isMatch( "define", "*def*" ), True )
    assert_check( isMatch( "define", "def*" ), True )
    assert_check( isMatch( "it's defined", "def*" ), False )
    assert_check( isMatch( "it's defined", "*def*" ), True )
        
    assert_check( isMatchFillVar( "Salut, je m'appelle Alexandre et je suis content!", "*appelle $name *" ), (True, {"$1":"Salut, je m'", "name":"Alexandre", "$2": "et je suis content!"} ) )
    assert_check( isMatchFillVar( "My adress is 12 Candiotti street.", "My $attribute is $value." ), (True, {'attribute': 'adress', 'value': '12 Candiotti street'} ) )
    assert_check( isMatchFillVar( "My bizness is 43 Main street", "My $attribute is $value" ), (True,  {'attribute': 'bizness', 'value': '43 Main street'} ) )
            
if __name__ == "__main__":
    autoTest();