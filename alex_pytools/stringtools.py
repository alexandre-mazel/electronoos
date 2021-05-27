# -*- coding: utf-8 -*-
"""
some classic handy classes to work on string
(c) 2010-2022 A. Mazel
"""        
def assert_equal( a, b ):
    print( "%s != %s ?" % (str(a),str(b)) )
    if a!=b:
        assert(0)

def findSubString( buf, strBefore, strAfter= "", nOccurence = 1, bQuiet=False ):
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
    if not bQuiet: print("DBG: findSubString: looking for '%s' in '%s...' return nothing (idx:%s) (before:'%s'), (after:'%s')" % (strBefore,buf[:40],idx,strBefore,strAfter) )
    return ""
    
def timeCompareSubString(nTimes):
    import time
    import re
    ss,se = "salut","enfants"   # time for 1000 loops (finsubstring-RE): ms4 / RPI3 2.7--3.8 / linux
    s1 = "salut les enfants"                       # 0.002-0.003         /  0.018-0.031 -- 0.022-0.032
    s2= "#"*1000000+s1                           # 0.30-0.38                / 3.64-11.60 -- 3.66-8.13
    s3= s1 + "#"*10000000                       # 4.86-0.003            / 27.8-0.029 -- 27.8-0.029
    s4= "#"*100000+s1+"#"*10000000     # 4.86-0.040             / 28.0-1.20 -- 28.2-0.849 
    s5= s4*4                                            # 20.0-040                  / 112-1.17 -- 112-0.746
    for s in [s1,s2,s3,s4,s5]:
        timeBegin = time.time()
        #~ print(s)
        for i in range(nTimes):
            out = findSubString(s,ss,se,bQuiet=True)
        duration = time.time()-timeBegin
        print("findSubString: %5.3fs" % duration )
        timeBegin = time.time()
        
        for i in range(nTimes):
            out = re.search(ss + "(.*?)" + se, s).group(1)
        duration = time.time()-timeBegin
        print("RE: %5.3fs" % duration )    
#~ timeCompareSubString(1000)
    
assert_equal(findSubString("Alexandre est content oui", "Alexandre ", " content"), "est")
assert_equal(findSubString("Alexandre est content oui", "content ", "blabla"), "oui")

assert_equal(findSubString("Alexandre est content", "Alexandre "), "est content")
