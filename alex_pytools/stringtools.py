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
    
    
def removeAccent( c ):
    bVerbose = 1
    try:
        acc="ÁÉÈÎÍÓÖÙâàáãäåçéêëèîïíìñôóòðöøõûüùúŷÿ" # TODO A avec accent
        noacc="AEEIIOOUaaaaaaceeeeiiiinooooooouuuuyy"
        #~ idx=acc.find(c) # in python 2.7: UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 0: ordinal not in range(128) // ord(value) was 233
        #~ if idx != -1:
            #~ return noacc[idx]
        #~ for i in range(len(acc)):
            #~ if c == acc[i]:
                #~ return noacc[i]
        if 0:
            # generate acc_ord code value
            for c in acc:
                print("%s," % ord(c) )
                
        acc_ord = [
            193, # A
            201,
            200,
            206, # premier I
            205,
            211, # premier O
            214,
            217, # premier U
            226,
            224,
            225,
            227,
            228,
            229, #dernier a
            
            231,
            233,
            234,
            235,
            232,
            238,
            239,
            237,
            236, # dernier i
            241,
            244,
            243,
            242,
            240,
            246,
            248,
            245, #dernier o
            251,
            252,
            249,
            250, # dernier u
            375,
            255,
            ]

        # same chars at ovh (preceded by a 195 or 197 in front of 183)
        acc_ord_ovh = [
            129, # A untested
            137,
            136,
            142, # premier I
            141,
            147, # premier O
            150,
            153, # premier U
            162,
            160,
            161,
            163,
            164,
            165, #dernier a
            
            167,
            169,
            170,
            171,
            168,
            174,
            175,
            173,
            172, #dernier i
            177,
            180,
            179,
            178,
            176,
            182,
            184,
            181, # dernier o
            187,
            188,
            185,
            186, #dernier u
            183,
            191,
        ]

        #~ assert_equal( len(acc_ord),len(noacc) )
        for i in range(len(acc_ord)):
            if ord(c) == acc_ord[i]:
                return noacc[i]        

        #~ assert_equal( len(acc_ord),len(acc_ord_ovh) )
        for i in range(len(acc_ord_ovh)):
            if ord(c) == acc_ord_ovh[i]:
                return noacc[i]      
                
        if c == "æ" or ord(c)==230:
            c = "ae"
        elif c == "Æ" or ord(c)==198:
            c = "AE"
        elif c == "œ" or ord(c)==339:
            c = "oe"
        elif c == "Œ" or ord(c)==338:
            c = "OE"
        elif ord(c) == 194: # A circ
            c = "A"
        elif ord(c) == 199: # C cedile
            c = "C"
        elif ord(c) == 231: # c cedile not detected previously
            c = "c"
        elif ord(c) == 203: # E trema
            c = "E"
        elif ord(c) == 207: # I trema
            c = "I"
        elif ord(c) == 212: # O circ
            c = "O"
        elif ord(c) == 156 or ord(c) == 140:
            # second part of oe, don't complain (minuscule then majuscule)
            c = ""
        elif ord(c) == 195 or ord(c) == 197:
            # mark of char on two chars at ovh, don't complain
            c = ""
        elif ord(c) == 222 or ord(c) == 254:
            # truc bizarre qui ressemble a une barre avec un demi cercle dessus
            c = ""
        elif ord(c) == 8211 or ord(c) == 8212:
            # custom hyphen
            c = "-"
        elif ord(c) == 8216 or ord(c) == 8217:
            # type de '
            c = "'"
        elif ord(c) == 8220 or ord(c) == 8221:
            # type de  "
            c = '"'
        elif ord(c) == 8226:
            # type de boule
            c = '.'
        elif ord(c) == 8230:
            c = "..."
        elif ord(c) == 8364:
            c = "euros"
        else:
            try:
                if bVerbose: print("DBG: stringtools.removeAccent: not found: %c (%s)" % (c,ord(c) ))
            except BaseException as err:
                print("DBG: stringtools.removeAccent: catch else: ord: %s, err: %s" % (ord(c),err) )
            c="" # it should remains only invisible char like the square before "oe"
        return c
    except TypeError as err:
        print("DBG: stringtools.removeAccent: type error: '%s' char:%s, returning '_'" % (c,str(err)) )
    return "_"

    


if __name__ == "__main__":
    #~ timeCompareSubString(1000)
    
    assert_equal(findSubString("Alexandre est content oui", "Alexandre ", " content"), "est")
    assert_equal(findSubString("Alexandre est content oui", "content ", "blabla"), "oui")

    assert_equal(findSubString("Alexandre est content", "Alexandre "), "est content")
    assert_equal(accentToHtml("Un élève épatant à Noël"), "Un &eacute;l&egrave;ve &eacute;patant &agrave; No&euml;l")

    
    assert_equal(removeAccent("é"),"e")
    assert_equal(removeAccent("Ï"),"I")
    assert_equal(removeAccent("€"),"euros")