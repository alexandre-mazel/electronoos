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
        if c == "Æ" or ord(c)==198:
            c = "AE"
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
        elif ord(c) == 222 or ord(c) == 254:
            # truc bizarre qui ressemble a une barre avec un demi cercle dessus
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
        """
        A la main, j'ai effacé du fichier:
        sans;m;;1715.23
        sens;f;;331.35
        Et j'ai ajouté:
        corto
        """
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
            # some name are doubbled, eg; Jean (1) and Jean (2)
            if '(' in strFirstname:
                strFirstname = strFirstname.split('(')[0]
                #~ print("strFirstname: '%s'" % strFirstname )
                strFirstname = strFirstname.strip()
            bFemale = strGender == 'f'
            listCountries = strCountry.split(',')
            listCountries = [k.strip() for k in listCountries]
            strOccurence = strOccurence.replace("\n", "" )
            rOccurence = float(strOccurence)
            #~ print(strFirstname)
            k = simpleString(strFirstname)
            if k in self.dictFirstname.keys():
                if bVerbose: print("WRN: Firstnames.load: forgetting dubbled %s (perhaps due to various accent simplified)" % (k) )
            else:
                self.dictFirstname[k] = (strFirstname, bFemale, tuple(listCountries), rOccurence)
            
    def get( self, strFirstname ):
        """
        return (strFirstname, bFemale, tupleCountries, rOccurence) 
        or None if not found
        """
        try:
            k = simpleString(strFirstname)
            return self.dictFirstname[k]
        except KeyError as err:
            return None
            
    def getCompound( self, strFirstname ):
        """
        search for compound firstname, eg: Jean-Bernard
        return a construction with minimal of less use firstname div by number of firstname
        return None if at least one firstname is not a known one
        """
        listFirstName = strFirstname.replace('-', ' ')
        listFirstName = listFirstName.split(' ')
        minOcc = 150
        firstAnswer = None
        for f in listFirstName:
            #~ print("DBG: getCompound: checking '%s'" % f )
            res = self.get(f)
            if res == None:
                #~ print("DBG: getCompound: checking '%s' => not found" % f )
                return None
            if firstAnswer == None:
                firstAnswer = res
            occ = res[3]
            if occ < minOcc:
                minOcc = occ
        return firstAnswer[:-1]+(minOcc,)
        
    def printListByOcc( self ):
        out = sorted(self.dictFirstname.values(),key=lambda x: x[3],reverse=True)
        for e in out:
            print(e)

# class Firstnames - end
firstnames = Firstnames()
firstnames.load()
#~ firstnames.printListByOcc()

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
    
    val = firstnames.get( "Jean" )
    assert_equal( val[0], "Jean" )
    
    val = firstnames.get( "abdul-aziz" )
    assert_equal( val[0], "Abdul-aziz" )
    
    
    val = firstnames.get( "Tutu" )
    assert_equal( val, None )
    
    val = firstnames.get( "Jean-René" )
    assert_equal( val, None )

    val = firstnames.get( "De" )
    assert_equal( val, None )

    val = firstnames.get( "Íde" )
    assert_equal( val[0], "Íde" )    
    

    val = firstnames.getCompound( "Jean-Bernard" )
    assert_equal( val[0], "Jean" )
    assert_equal( val[1], False )
    assert_equal( val[3], 0.0 )

    val = firstnames.getCompound( "Jean-René" )
    assert_equal( val[0], "Jean" )
    assert_equal( val[1], False )
    assert_equal( val[3], 0.0 )
    
    val = firstnames.getCompound( "Jean René" )
    assert_equal( val[0], "Jean" )
    assert_equal( val[1], False )
    assert_equal( val[3], 0.0 )
    
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
