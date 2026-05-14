import sys

"""
tempo method to explore a big file
"""

sys.path.append("c:/users/alexa/dev/git/obo/spider/")
import retrieve_pop3

def printBuffer(buffer):
    lines = retrieve_pop3.splitBytes(buffer,ord("\n"))
    
    nNbrOutputted = 0
    nNbrSkipped = 0
    for line in lines:
        if len(line)>70  \
            and ord(' ') not in line \
            and ord(',') not in line \
            and ord('-') not in line \
            and ord(':') not in line \
            and ord(';') not in line \
            and ord('\t') not in line \
            :
                #~ print("DBG: skipping: %s" % line )
                nNbrSkipped += 1
                continue # les lignes de b64 n'ont pas d'espaces on les skippe...
                
        if nNbrSkipped>0:
            print("! skipped %d line(s)" % nNbrSkipped )
            nNbrSkipped = 0
        print(line)
        nNbrOutputted += 1
        if nNbrOutputted>1000:
            break
        
def showPartBigFile(filename,offset,nSizeContext=1000):
    f = open(filename,"rb")
    start = offset
    size = nSizeContext
    bShowBefore = 0
    if bShowBefore:
        start -= nSizeContext
        size += nSizeContext
    f.seek(start,0)
    buf = f.read(size)
    f.close()
    printBuffer(buf)
        

def searchStringInBigFile(filename,motif,nSizeContext=1000):
    """
    search a string in a big file, print it and the surrounding context
    - motif: string to find
    """
    f = open(filename,"rb")
    nPacketSize = 1024*1024*50 # need to be larger than 2*nSizeContext
    nTotalRead = 0
    motif_binary = motif.encode("cp1252")
    while 1:
        print("INF: offset: %s (%dMB)\r" % (nTotalRead,nTotalRead//1024//1024),end="" )
        buf = f.read(nPacketSize)
        nTotalRead += len(buf)
        idx = buf.find(motif_binary)
        if idx != -1:
            offset = nTotalRead-len(buf)+idx
            print("\nINF: searchStringInBigFile: motif found at offset: %s\n" % offset)
            start = idx-nSizeContext
            end = idx+nSizeContext
            if start<0:
                f.seek(start,1) # rewind a bit
                buf = f.read(nSizeContext*2)
                start = 0
                end = nSizeContext*2
            if end>len(buf):
                offset = len(buf)-idx-nSizeContext
                f.seek(-offset,1) # rewind a bit
                start = 0
                end = nSizeContext*2                
                
            b = buf[start:end]
            printBuffer(b)

            break
    
    
f = "D:/takeout_google_zelma (ext)/Tous les messages, y compris ceux du dossier Spam -055.mbox"
#~ s = "From 1614052608291360005@xxx Thu Oct 11 17:55:17 +0000 2018"
s = "2018 19:54:50"
s = "Subject: La petit chanteuse allemande"
nSizeContext=20000
nSizeContext=40000
#~ nSizeContext=1024*1024*10
#~ searchStringInBigFile(f,s,nSizeContext=nSizeContext) # we will print only interesting lines

offset = 2635129925
offset = 11136184000

nSizeContext=1024*1024*10
nSizeContext=10000
showPartBigFile(f,offset,nSizeContext=nSizeContext)
