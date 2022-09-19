# -*- coding: cp1252 -*-

import sys

def diffShow(s1,s2,nNbrDiffMax = 5):
    """
    affiche les premieres différences de 2 chaines
    """
    if len(s1) != len(s2):
        print("WRN: different size: %d and %s" % (len(s1),len(s2)) )
        
    i = 0
    nDiff = 0
    nLenToShow = 40
    while i < len(s1):
        if s1[i] != s2[i]:
            start = max(0,i-20)
            print("diff %d:\n  %s\n  %s\n" % (nDiff, s1[start:i+nLenToShow],s2[start:i+nLenToShow]))
            i += nLenToShow # here we should try to resync... (jump nLenToShow or 16 then find next sequence of 10 char same in both s)
            nDiff += 1
            if nDiff > nNbrDiffMax:
                break
        i += 1

def diffShowFiles(f1,f2):
    f = open(f1,"r")
    s1 = f.read()
    f.close()
    f = open(f2,"r")
    s2 = f.read()
    f.close()
    return diffShow(s1,s2)
    
if len(sys.argv)<3:
    print("\nthis script will show the 5 first difference between two files\nsyntaxe: diff file1 file2\n")
    
f1 = sys.argv[1]
f2 = sys.argv[2]
diffShowFiles(f1,f2)