# -*- coding: utf-8 -*-
"""
some classic handy classes to work on string
(c) 2010-2022 A. Mazel
"""        
def assert_equal( a, b ):
    print( "%s != %s ?" % (str(a),str(b)) )
    if a!=b:
        assert(0)

def findSubString( buf, strBefore, strAfter= "", nOccurence = 1 ):
    """
    return the first string between strBefore and strAfter
    nOccurence: return the nth found
    """
    idx = 0
    count = 0
    while 1:
        idx = buf[idx:].find(strBefore)
        if idx == -1:
            break
        count += 1
        idx = idx+len(strBefore)
        if count == nOccurence:
            if strAfter == "":
                idxEnd = -1
            else:
                idxEnd = buf[idx:].find(strAfter)
            if idxEnd == -1:
                s = buf[idx:]
            else:
                s = buf[idx:idx+idxEnd]
        return s
    print("DBG: findSubString: looking for '%s' return nothing (idx:%s)" % (strBefore,idx) )
    return ""
    
assert_equal(findSubString("Alexandre est content oui", "Alexandre ", " content"), "est")
assert_equal(findSubString("Alexandre est content oui", "content ", "blabla"), "oui")

assert_equal(findSubString("Alexandre est content", "Alexandre "), "est content")
