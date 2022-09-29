# -*- coding: cp1252 -*-

import io
import sys

"""

Ce qui fonctionne:

source encoding                         cp1252                       utf-8
loading encoding                    cp         utf                  cp          utf

python 2 - literal                    0            ~cp                0               ~utf-8
python 2 - literal avec u           0             1                     0             0
python 2 - literal *u                 0
python 2 - literal *c                  0            1
python 2 - literal avec u+u       ~c         ~u
python 2 - literal avec u+c       0          ~c


python 3 - literal                 0            1                   0              0
python 3 - literal avec u       0            1                      0             0

"""

"""
# TODO: tester ce module a l'occasion:
import codecs
f = codecs.open('out.txt', mode="w", encoding="iso-8859-1")
"""

def assert_equal(a,b):
    bPrintParam = 0
    #~ bPrintParam = 1
    if a == b:
        print("(%s==%s) =>\nOK\n" % (a,b))
        return
    if sys.version_info[0]<3:
        au = a
        bu = b
        if isinstance(a,unicode):
            print("assert_equal: 1st param is unicode")
            au = a.encode("utf-8", 'replace')

        if isinstance(b,unicode):
            print("assert_equal: 2nd param is unicode")
            bu = b.encode("utf-8", 'replace')
        
        if au == bu:
            if bPrintParam: print("(%s==%s) =>\nOK (but unicode_encoded with utf-8)" % (a,b))
            print("~OK (but unicode_encoded with utf-8)\n")
            return
            
    if sys.version_info[0]<3:
        au = a
        bu = b
        if isinstance(a,unicode):
            print("assert_equal: 1st param is unicode")
            au = a.encode("cp1252", 'replace')

        if isinstance(b,unicode):
            print("assert_equal: 2nd param is unicode")
            bu = b.encode("cp1252", 'replace')
        
        if au == bu:
            if bPrintParam: print("(%s==%s) =>\n~OK (but unicode_encoded with cp1252)" % (a,b))
            print("~OK (but unicode_encoded with cp1252)\n")
            return
            
    if bPrintParam: print("(%s==%s) =>\nNOT ok (type:%s and %s)" % (a,b,type(a),type(b)))
    print("NOT ok\n")
    #~ assert(0)

def loadAccentuatedFile(filename):
    file = io.open(filename,"rt", encoding="utf-8")
    buf = file.read()
    file.close()
    return buf
    
buf = loadAccentuatedFile( "file_with_accent_windows.txt" )

try:
    print("test +c:")
    assert_equal( buf, "J'ai dépensé 18€ pour payer une glace à un élève.".encode("cp1252") )
except:
    print("param erreur")
try:
    print("test -c:")
    assert_equal( buf, "J'ai dépensé 18€ pour payer une glace à un élève.".decode("cp1252") )
except:
    print("param erreur")
    
try:
    print("test +u:")
    assert_equal( buf, "J'ai dépensé 18€ pour payer une glace à un élève.".encode("utf-8") )
except:
    print("param erreur")
try:
    print("test -u:")
    assert_equal( buf, "J'ai dépensé 18€ pour payer une glace à un élève.".decode("utf-8") )
except:
    print("param erreur")
    
    
print("test u+c:")
assert_equal( buf, (u"J'ai dépensé 18€ pour payer une glace à un élève.").encode("cp1252") )
print("test u+u:")
assert_equal( buf, (u"J'ai dépensé 18€ pour payer une glace à un élève.").encode("utf-8") )
print("test u:")
assert_equal( buf, u"J'ai dépensé 18€ pour payer une glace à un élève." )
print("test rien:")
assert_equal(buf, "J'ai dépensé 18€ pour payer une glace à un élève." )
#~ print("TEST PASS [OK]")
