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
    import sys
    import struct
    import multiprocessing
    print( "python version   : %d.%d.%d (%dbits) (%d core(s))" % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro,8 * struct.calcsize("P"),multiprocessing.cpu_count()) )
    
    ss,se = "salut","enfants"   # time for 1000 loops (finsubstring-RE): MSTab4 3.8-32b / RPI3 2.7-32b--3.5-32b             / Xenia 3.8-32b
    s1 = "salut les enfants"                                                       # 0.002-0.003        /  0.018-0.031 -- 0.022-0.032   / 0.000- 0.001
    s2= "#"*1000000+s1                                                            # 0.30-0.38             / 3.64-11.60 -- 3.66-8.13             / 0.105-0.182
    s3= s1 + "#"*10000000                                                        # 4.86-0.003           / 27.8-0.029 -- 27.8-0.029        / 0.400-0.001
    s4= "#"*100000+s1+"#"*10000000                                      # 4.86-0.040           / 28.0-1.20 -- 28.2-0.849          / 0.379-0.019
    s5= s4*4                                                                             # 20.0-040               / 112-1.17 -- 112-0.746               / 11.7-0.019
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
        
        
accToHtml = [
                ["á","aacute"],
                ["à","agrave"],
                ["â","acirc"],
                ["ä","auml"],
                ["ã","atilde"],
                ["å","aring"],

                ["é","eacute"],
                ["è","egrave"],
                ["ê","ecirc"],
                ["ë","euml"],

                ["í","iacute"],
                ["ì","igrave"],
                ["î","icirc"],
                ["ï","iuml"],

                ["ó","oacute"],
                ["ò","ograve"],
                ["ô","ocirc"],
                ["ö","ouml"],

                ["ú","uacute"],
                ["ù","ugrave"],
                ["û","ucirc"],
                ["ü","uuml"],                    
            ]
            
def accentToHtml(s):
    """
    change a string to the same with accent transformed to html
    """

                
    #~ for c in s:
        #~ print("%s %d" % (c,ord(c)) )

        
    for acc,norm in accToHtml:
        #~ print("acc: %s %d" % (acc,ord(acc)) )
        s = s.replace(acc,"&"+norm+";")
        #s = s.replace(acc.decode('cp1252').encode('utf-8'),norm) # as this source ile is ascii encoded
        
    #~ print("killAccent: return: %s" % s )
    return s

if __name__ == "__main__":
    #~ timeCompareSubString(1000)
    
    assert_equal(findSubString("Alexandre est content oui", "Alexandre ", " content"), "est")
    assert_equal(findSubString("Alexandre est content oui", "content ", "blabla"), "oui")

    assert_equal(findSubString("Alexandre est content", "Alexandre "), "est content")
    assert_equal(accentToHtml("Un élève épatant à Noël"), "Un &eacute;l&egrave;ve &eacute;patant &agrave; No&euml;l")
