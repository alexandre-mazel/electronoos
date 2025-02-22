# -*- coding: utf-8 -*-

import re
import sys

try: from misctools import assert_equal
except: pass

"""
some classic handy classes to work on string
(c) 2010-2022 A. Mazel
"""        

def lowerList( l ):
    o = []
    for s in l:
        o.append(s.lower())
    return o

def findSubString( buf, strBefore, strAfter= "", nOccurence = 1, bQuiet=False ):
    """
    return the first string between strBefore and strAfter
    nOccurence: return the nth found (require nth-1 strAfter to be found before)
    """
    idx = 0
    count = 0
    while 1:
        idxFind = buf[idx:].find(strBefore)
        if idxFind == -1:
            break
        idx = idxFind+idx # because it was relative to idx:
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
        if strAfter != "":
            idxEnd = buf[idx:].find(strAfter)
            if idxEnd == -1:
                break # we have finished
            idx = idx+idxEnd+len(strAfter)
            #~ print("DBG: findSubString: apres count, new substring: %s..." % (buf[idx:idx+40]))
            
    if not bQuiet: print("DBG: findSubString: looking for '%s' in '%s...' return nothing (idx:%s) (before:'%s'), (after:'%s')" % (strBefore,buf[:40],idx,strBefore,strAfter) )
    return ""
    
def findSubStringToList( buf, strBefore, strAfter ):
    """
    return all strings contain between two sepas strBefore and strAfter
    """
    o = []
    occ = 1
    while 1:
        s = findSubString(buf,strBefore,strAfter,occ)
        if s == "":
            break
        o.append(s)
        occ += 1
    return o
    
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
        
   
"""           
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
    # change a string to the same with accent transformed to html

    #~ for c in s:
        #~ print("%s %d" % (c,ord(c)) )

    if sys.version_info[0] >= 3:
        # ne fonctionne pas sur python2.x:
        # s = s.replace(acc,"&"+norm+";") =>
        # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 0: ordinal not in range(128)
        for acc,norm in accToHtml:
            #~ print("acc: %s %d" % (acc,ord(acc)) )
            s = s.replace(acc,"&"+norm+";")
            #s = s.replace(acc.decode('cp1252').encode('utf-8'),norm) # as this source ile is ascii encoded
    else:
        o = ""
        for c in s:
            for tr in accToHtml:
                print("comp %s and %s" % (c,tr[0]))
                if c == tr[0]:
                    o += "&"+tr[1]+";"
                    break
            else:
                o += c
        s = o
        
    #~ print("accentToHtml: return: %s" % s )
    return s
"""

# generated by stringtools_generate_accent_table.py
# objectif: work whatever the encoding of this file!
accented = [
    0xc0, # &Agrave;
    0xe0, # &agrave;
    0xc2, # &Acirc;
    0xe2, # &acirc;
    0xe7, # &ccedil;
    0xc9, # &Eacute;
    0xca, # &Ecirc;
    0xc8, # &Egrave;
    0xcb, # &Euml;
    0xe9, # &eacute;
    0xea, # &ecirc;
    0xe8, # &egrave;
    0xeb, # &euml;
    0x20ac, # &euro;
    0xce, # &Icirc;
    0xee, # &icirc;
    0xd4, # &Ocirc;
    0xf4, # &ocirc;
    0xdb, # &Ucirc;
    0xfb, # &ucirc;
    0xf9, # &ugrave;
    0x26, # &amp;
    0x3c, # &lt;
    0x3e, # &gt;
    0x22, # &quot;
    0x27, # &#39;
    0x92, # &#39;
    0x91, # &#39;
    0x94, # &quot;
    0x93, # &quot;
    0xa, # %0D%0A
    0x20, # %20
    0x3f, # %3F
    0xa0, # %20
    0xab, # &quot;
    0xbb, # &quot;
]

import stringtools_generate_accent_table
htmlled = stringtools_generate_accent_table.htmlled

accented_first_no_accent = stringtools_generate_accent_table.accented_first_no_accent
                    
    
def cp1252ToHtml(s, bOnlyAccent=False):
    
    #~ trans = [
                    #~ ["à","&agrave;"],
                    #~ ["ç","&ccedil;"],
                    #~ ["é","&eacute;"],
                    #~ ["ê","&ecirc;"],
                    #~ ["è","&egrave;"],
                    
                    #~ ["€","&euro;"],
                    
                    #~ ["ô","&ocirc;"],
                #~ ]
                        
    #~ print("accented: %d" % len(accented))
    #~ print("htmlled: %d" % len(htmlled))
    o = ""
    for c in s:
        #~ print("ord: 0x%x char: %s" % (ord(c),c))
        try:
            i = accented.index(ord(c))
            if not bOnlyAccent or i < accented_first_no_accent:
                o += htmlled[i]
            else:
                o += c
            
        except ValueError:
            o += c
            if ord(c)>127:
                print("WRN: cp1252ToHtml: unhandled char: 0x%x => %s" % (ord(c),c))
    #~ return o.replace("\n","%0D%0A") # specific case as \n is two chars
    return o
    
def htmlToCp1252(s):
    """
    "un%20&eacute;leve" => "un eleve"
    not optimal !
    """
    
    #~ trans = [
                    #~ ["à","&agrave;"],
                    #~ ["ç","&ccedil;"],
                    #~ ["é","&eacute;"],
                    #~ ["ê","&ecirc;"],
                    #~ ["è","&egrave;"],
                    
                    #~ ["€","&euro;"],
                    
                    #~ ["ô","&ocirc;"],
                #~ ]
                        
    #~ print("accented: %d" % len(accented))
    #~ print("htmlled: %d" % len(htmlled))
    o = s
    for i,motif in enumerate(htmlled):
        o = o.replace(motif,accented[i])
    return o
    
def accentToHtml(s):
    return cp1252ToHtml(s,bOnlyAccent=True)
    
def removeAccent( c ):
    """
    receive a char more than 127 and handle it
    """
    bVerbose = 1
    bVerbose = 0
    if bVerbose: print("INF: stringtools.removeAccent: entering with a char len: %d, starting with ord: %d, char: %s" % (len(c),ord(c[0]),c))
    try:
        
        if sys.version_info[0] < 3:
            if len(c)>1:
                print("DBG: stringtools.removeAccent: received many chars:")
                for i in c:
                    print("    ord: %d" % ord(i))
                if ord(c[0]) == 195:
                    # some are same in python3
                    if bVerbose: print("DBG: stringtools.removeAccent: recurse")
                    ret = removeAccent(c[1])
                    if ret != "":
                        return ret
                
                # handle current first ord
                tabconvPerKey0 = {
                            130: [
                                        (172, "euros"),
                            ],
                            195: [
                                        (143, "I"), # I trema en python2.7
                                        (134, "AE"),
                                        (166, "ae"),
                            ],
                            197: [
                                        (146, "OE"),
                                        (147, "oe"),
                            ],
                    }
                o = ord(c[0])
                try:
                    tabconv = tabconvPerKey0[o]
                    o = ord(c[1])
                    for conv in tabconv:
                        if conv[0] == o:
                            return conv[1]
                except KeyError as err:
                    pass
                    

                # handle flavoured combination
                tabconv = [
                                ((226,130,172), "euros")
                        ]
                listOrd = []
                for i in c:
                    listOrd.append(ord(i))
                listOrd=tuple(listOrd)
                for conv in tabconv:
                    if conv[0] == listOrd:
                        return conv[1]
                print("DBG: stringtools.removeAccent: unhandled symbol:")
                print("%s" % c)
                return ""
            
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
        
        if sys.version_info[0] >= 3:
            bFound = True
            if c == "æ" or ord(c)==230:
                c = "ae"
            elif c == "Æ" or ord(c)==198:
                c = "AE"
            elif c == "œ" or ord(c)==339:
                c = "oe"
            elif c == "Œ" or ord(c)==338:
                c = "OE"
            else:
                bFound = False
            if bFound:
                return c
                
        if ord(c) == 194: # A circ
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
            c = "" # it could remains only invisible char like the square before "oe"
        return c
    except KeyError as err:
        print("DBG: stringtools.removeAccent: type error: '%s' char:%s, returning '_'" % (c,str(err)) )
    return "_"
# removeAccent - end

def removeAccentString( s ):
    out = ""
    for c in s:
        if ord(c)>127:
            c = removeAccent(c) # WARNING: in python2.7 this method will cut extra char in two char, and so they won't be detected correctly
            #~ print("DBG: removeAccentString: received '%s'" % c )
        out += c
    return out
    
        
def sizeToStr(v):
    listUnit = ['B','KB', 'MB', 'GB', 'TB']
    idxUnit = 0
    while v > 1024:
        v /= 1024
        idxUnit += 1
    if idxUnit == 0:
        return "%d%s" % (v,listUnit[idxUnit])
    return "%.1f%s" % (v,listUnit[idxUnit])
    
def timeToStr(ts):
    """
    take a time in sec and print it as it's best
    """
    if ts < 60:
        return "%2ds" % ts
    ts /= 60
    if ts < 60:
        return "%2dm" % ts     
    ts /= 60
    if ts < 24:
        return "%.1fh" % ts      
    ts /= 24
    return "%.1fd" % ts
    
def encodeAllToNumbered(s):
    """
    encode all char  >127 to their hexacode
    # never used!
    """
    o = ""
    for c in s:
        if ord(c)>127:
            o += "CHAR(%x)" % ord(c)
        else:
            o +=c
    return o

#~ print(encodeAllToNumbered("élève"))

def cutSentenceToWords( s ):
    """
    return a list of words in sentence, removing all punctuation
    c'est bien => ["c", "est", "bien"]
    """
    if 0:
        return re.split('\W+',s) # to add other char: \W+|_ ( a tester)
        
    words = []
    i = 0
    ibegin = 0
    lens = len(s)
    while i < lens:
        c = s[i]
        if c in " ,:;.'\"!?-()":
            if i-ibegin>0:
                words.append(s[ibegin:i])
            ibegin = i+1
        i += 1
    if ibegin < i:
        words.append(s[ibegin:i])
    return words

if __name__ == "__main__":
    if 0:
        # measure perf
        s = "c'est bien"
        import time
        pattern = re.compile('\W+')
        timeBegin = time.time()
        for i in range(1000000):
            #~ s.split() # best: 0.127 ' mais ne coupe que les espaces
            cutSentenceToWords(s) # best: 1.173 avant ajout '!?': best 1.108 (si cut que sur ' ' best: 1.044)
            #~ re.split('\W+',s) # best: 1.146 avg ~ 1.28
            #~ pattern.split(s) # best: 0.720
            
        print("duration: %.3f" % (time.time()-timeBegin) )
        exit(0)
    
def transformAccentToUtf8( s ):
    """
    transform a string from cp1252 to utf8
    """
    s = cp1252ToHtml(s)
    # this file is encoded in utf8, so the accent in real will be ok
    # todo: better! avec une table utf8
    s = s.replace("&eacute;","ai")
    s = s.replace("&egrave;","ai")
    s = s.replace("&ecirc;","ai")
    s = s.replace("%20"," ")
    s = s.replace("&#39;","'")
    s = s.replace("&agrave;","a")
    return s



if __name__ == "__main__":
    #~ timeCompareSubString(1000)
    
    assert_equal(findSubString("Alexandre est content oui", "Alexandre ", " content"), "est")
    assert_equal(findSubString("Alexandre est content oui", "content ", "blabla"), "oui")
    assert_equal(findSubString("Alexandre est content et il est super et il est jaune et il est bleu.", "est ", " et",1), "content")
    assert_equal(findSubString("Alexandre est content et il est super et il est jaune et il est bleu.", "est ", " et",2), "super")
    assert_equal(findSubString("Alexandre est content et il est super et il est jaune et il est bleu.", "est ", " et",3), "jaune")
    assert_equal(findSubString("Alexandre est content et il est super et il est jaune et il est bleu.", "est ", " et",4), "bleu.") #fin not found => jusqu'a la fin de la phrase
    assert_equal(findSubString("Alexandre est content et il est super et il est jaune et il est bleu.", "est ", " et",5), "")
    
    assert_equal(findSubString("Alexandre est content, et super et jaune et bleu.", "est ", " et",2), "")
    assert_equal(findSubString("Alexandre est content, et super et jaune et bleu.", "et ", "",2), "jaune et bleu.") # discutable, pourquoi le '.' est apparue a la fin?

    assert_equal(findSubString("Alexandre est content", "Alexandre "), "est content")
    assert_equal(accentToHtml("Un élève épatant à Noël"), "Un &eacute;l&egrave;ve &eacute;patant &agrave; No&euml;l")

    
    #~ assert_equal(removeAccent("a"),"a") # normal case: no: removeAccent work only on accentuated accent
    assert_equal(removeAccent("é"),"e")
    assert_equal(removeAccent("Ï"),"I")
    assert_equal(removeAccent("€"),"euros")
    assert_equal(removeAccent("æ"),"ae")
    assert_equal(removeAccent("Æ"),"AE")
    assert_equal(removeAccent("œ"),"oe")
    assert_equal(removeAccent("Œ"),"OE")
    assert_equal(removeAccentString("Jean-Pierre"),"Jean-Pierre")
    assert_equal(removeAccentString("Frédéric"),"Frederic")
    if sys.version_info[0] < 3:
        assert_equal(removeAccentString(u"100€"),"100euros")
    else:
        assert_equal(removeAccentString("100€"),"100euros")
        

    s = cutSentenceToWords("c'est bien")
    assert_equal( s, ["c", "est", "bien"])
    s = cutSentenceToWords("Le petit chien, dit 'ouah ouah'!")
    assert_equal( s, ['Le', 'petit', 'chien', 'dit', 'ouah', 'ouah'])
    
    print("INF: autotest passed [GOOD]")