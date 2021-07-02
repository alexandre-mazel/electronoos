

# solution: don't write \ followed by s!!!
def findGreaterCharInFile(strFilename, nLimit = 127):
    f = open(strFilename,"rt")
    f.seek(26111)
    while 1:
        buf = f.readline()
        print(buf,end = '')
        if buf == "":
            break
        bFound=False
        for i,c in enumerate(buf):
            if ord(c)>nLimit:
                print("char at position %d is too great: %d" %(i,ord(c)) )
                bFound = True
        if bFound:
            break
        break
    f.close()
    
    
findGreaterCharInFile("test_perf.py",nLimit=127)