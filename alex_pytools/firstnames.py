# -*- coding: utf-8 -*-

import os
import sys
import time

def assert_equal(a,b):
    if a == b:
        print("(%s==%s) => ok" % (a,b))
        return

    if type(a)==type(b):
        if isinstance(a,tuple):
            print("sametupe")
            if str(a) == str(b):
                print("('%s'=='%s') => ok" % (a,b))
                return
            
    print("(%s==%s) => NOT ok (type:%s and %s)\ndetail:\n%s\n%s" % (a,b,type(a),type(b), a,b))
    assert(0)

def assert_diff(a,b,diff=0.1):
    if abs(a-b)<diff:
        print("(%s diff %s < %s) => ok" % (a,b,diff))
    else:
        print("(%s diff %s < %s)) => NOT ok (type:%s and %s)" % (a,b,diff, type(a),type(b)))
        assert(0)
        
def openWithEncoding( filename, mode, encoding, errors = 'strict' ):
    if sys.version_info[0] < 3:
        import io
        return io.open( filename, mode, encoding=encoding, errors=errors )
    return open( filename, mode, encoding=encoding, errors=errors )
        
def removeAccent( c ):
    bVerbose = 0
    try:
        acc="ÉÈÎâàçéêëèîïôûüùŷÿ" # TODO A avec accent
        noacc="EEIaaceeeeiiouuuyy"
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
            201,
            200,
            206,
            226,
            224,
            231,
            233,
            234,
            235,
            232,
            238,
            239,
            244,
            251,
            252,
            249,
            375,
            255
            ]

        # same chars at ovh (preceded by a 195 or 197 in front of 183)
        acc_ord_ovh = [
            137,
            136,
            142,
            162,
            160,
            167,
            169,
            170,
            171,
            168,
            174,
            175,
            180,
            187,
            188,
            185,
            183,
            191
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
        if c == "œ" or ord(c)==339:
            c = "oe"
        elif c == "Œ" or ord(c)==338:
            c = "OE"
        elif ord(c) == 231: # c cedile not detected previously
            c = "c"
        elif ord(c) == 156 or ord(c) == 140:
            # second part of oe, don't complain (minuscule then majuscule)
            c = ""
        elif ord(c) == 195 or ord(c) == 197:
            # mark of char on two chars at ovh, don't complain
            c = ""
        elif ord(c) == 8211 or ord(c) == 8212:
            # custom hyphen
            c = "-"
        elif ord(c) == 8216 or ord(c) == 8217:
            # type de '
            c = "'"
        elif ord(c) == 8220:
            # type de 
            c = '"'
        elif ord(c) == 8230:
            c = "..."
        else:
            try:
                if bVerbose: print("DBG: removeAccent: not found: %c (%s)" % (c,ord(c) ))
            except BaseException as err:
                print("DBG: removeAccent: catch else: ord: %s, err: %s" % (ord(c),err) )
            c="" # it should remains only invisible char like the square before "oe"
        return c
    except TypeError as err:
        print("DBG: removeAccent:type error: %s, returning '_'" % str(err) )
    return "_"

    
def simpleString( s ):
    """
    change a string to lower case without accent and no hypen
    """
    bPrintResultForDebug = 0
    o = ""
    for c in s:
        if ord(c)>127:
            #~ print("in %s: %c" % (s,c) )
            c = removeAccent(c)
            #~ print("=> %c" % c )
            bPrintResultForDebug = 1
        elif c == '-':
            c = ' '
        c = c.lower()
        o += c
    #~ if bPrintResultForDebug: print("=> %s" % o )
    return o

class Firstnames:
    """
    get firstname and occurence
    and departement by region
    """
    def __init__( self ):
        #~ self.dictRegionId = {} # for each region, it's index
        self.dictFirstname = {} # firstname => firstname bien orthographiée, is_female, list pays usage, occurence
        
    def load( self ):
        print("INF: Firstnames.load: loading firstnames data...")
        bVerbose = 0
        strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
        #~ print("strLocalPath: " + strLocalPath)
        if strLocalPath == "": strLocalPath = '.'
        strFilename = strLocalPath + '/datas/firstname.csv'
        enc = 'utf-8'
        enc = 'cp1252'
        file = openWithEncoding(strFilename, "rt", encoding = enc)
        line = file.readline() # skip first line

        while 1:
            line = file.readline()
            if len(line)<1:
                break
            if bVerbose: print("DBG: Regions.load: line: %s" % str(line) )
            line = line.replace('"','')
            fields = line.split(';')
            if bVerbose: print("DBG: Regions.load: fields: %s" % str(fields) )
            strFirstname, strGender, strCountry, strOccurence = fields
            strFirstname = strFirstname[0].upper() + strFirstname[1:]
            bFemale = strGender == 'f'
            listCountries = strCountry.split(',')
            listCountries = [k.strip() for k in listCountries]
            strOccurence = strOccurence.replace("\n", "" )
            rOccurence = float(strOccurence)
            k = simpleString(strFirstname)
            self.dictFirstname[k] = (strFirstname, bFemale, tuple(listCountries), rOccurence)
            
    def get( self, strFirstname ):
        """
        return None if not found
        """
        try:
            k = simpleString(strFirstname)
            return self.dictFirstname[k]
        except KeyError as err:
            return None

# class Firstnames - end
firstnames = Firstnames()
firstnames.load()

def autotest():
    val = firstnames.get( "Alexandre" )
    assert_equal( val[0], "Alexandre" )
    assert_equal( val[1], False )
    assert_equal( val[2], ("french", "portuguese", "hungarian") )
    assert_diff( val[3], 18 )
    
    val = firstnames.get( "Frédéric" )
    assert_equal( val[0], "Frédéric" )
    assert_equal( val[1], False )
    
    val = firstnames.get( "Elsa" )
    assert_equal( val[0], "Elsa" )
    assert_equal( val[1], True )
    assert_equal( val[2], ('english', 'german', 'swedish') )
    assert_diff( val[3], 5.51 )
# autotest- end
    
if __name__ == "__main__":
    if 1:
        autotest()
    if 0:        
        """
        Syntaxe:
            [--output_html]
        """
        bOutputHtml = False
        if len(sys.argv)>1:
            bOutputHtml = True
         #~ NDEV
        #~ statByRegion( bOutputHtml = bOutputHtml )
