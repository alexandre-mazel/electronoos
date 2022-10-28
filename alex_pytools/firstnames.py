# -*- coding: utf-8 -*-

import os
import sys
import time

import stringtools

def assert_equal(a,b):
    if a == b:
        print("(%s==%s) => ok" % (a,b))
        return
            
    if sys.version_info[0]<3:
        if isinstance(a,unicode):
            a = a.encode("utf-8", 'replace')

        if isinstance(b,unicode):
            b = b.encode("utf-8", 'replace')
        
        if a == b:
            print("(%s==%s) => ok (but unicode_encoded)" % (a,b))
            return
    
    if type(a)==type(b):
        if isinstance(a,tuple):
            print("sametupe")
            if str(a) == str(b):
                print("('%s'=='%s') => ok" % (a,b))
                return
            
    print("(%s==%s) => NOT ok (type:%s and %s)\ndetail:\n%s\n%s" % (a,b,type(a),type(b), a,b))
    if 1:
        print("1st value:")
        for c in a:
            print(ord(c))
        print("2nd value:")
        for c in b:
            print(ord(c))
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
        

    
def simpleString( s ):
    """
    change a string to lower case without accent and no hyphen
    """
    bPrintResultForDebug = 0
    o = ""
    for c in s:
        if ord(c)>127:
            #~ print("in %s: %c" % (s,c) )
            c = stringtools.removeAccent(c)
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
            #~ if k in self.dictFirstname.keys(): # this line is very bad: it construct a list for keys then do a list search in it
            if k in self.dictFirstname: # this one is great: it looks in dict's key using hash
                if bVerbose: print("WRN: Firstnames.load: forgetting dubbled %s (perhaps due to various accent simplified)" % (k) )
            else:
                self.dictFirstname[k] = (strFirstname, bFemale, tuple(listCountries), rOccurence) # this line takes 99% of times on python2.7 (moreover in rpi)
            
        # ajout de certains prénoms normaux, mais oublié
        rDefaultOcc = 3
        listForgot = [
                            ("Karine", True, ["fr"]),
                        ]
        
        for data in listForgot:
            strFirstname, bFemale, listCountries = data[:3]
            
            if len(data)>3:
                rOccurence = data[3]
            else:
                rOccurence = rDefaultOcc
            k = simpleString(strFirstname)
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
timeBegin = time.time()
firstnames.load()
#~ firstnames.printListByOcc()

print("Loading takes: %.2fs" % (time.time()-timeBegin))
#  mstab7_2.7 : 2.01s
#  mstab7_3.9 : 0.04s
# RPI4_2.7      : 12.93s
# RPI4_3.7      :  0.2s
# after removing the k in d.keys():
#  mstab7_2.7 : 0.06s
#  mstab7_3.9 : 0.04s
# RPI4_2.7      : 0.24s
# RPI4_3.7      :  0.2s

def autotest():
    # in python2, type that in the shell before:
    # set PYTHONIOENCODING=UTF-8
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
    
    val = firstnames.get( "Karine" )
    assert_equal( val[0], "Karine" )
    assert_equal( val[1], True )
    

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

    val = firstnames.getCompound( "Juliana" )
    assert_equal( val[0], "Juliana" )
    
    line = "hell- ° CV envoyé par HelloWork. Contient des données personnelles : ne pas utiliser, diffuser, copier sans le consentement de son auteur.Wurk"
    for w in line.split():
        ret = firstnames.getCompound(w)
        assert( ret is None )
    
    
    # time computeGender
    timeBeginStuff = time.time()
    for i in range(100000):
        firstnames.getCompound( "notexistant" )
        firstnames.getCompound( "Jean René" )
    duration = time.time()-timeBeginStuff
    print("time ComputeGender: %.3fs" % (duration) )
    assert(duration<1.2)
    
    print("INF: autotest passed [GOOD]")
    
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
