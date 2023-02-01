import os
import sys


strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import nettools

def saveImageFromPage(pagelocalfilename,websiteorigin = "", dst = '/tmp/'):
    f = open(pagelocalfilename,"rt")
    buf = f.read()
    f.close()
    cpt = 0
    while 1:
        start = '<img src="'
        idx = buf.find( start )
        if idx == -1:
            break
        buf = buf[idx+len(start):]
        idx2 = buf.find( '"' )
        addr = buf[:idx2]
        print("addr: '%s'" % addr)
        
        startalt = 'alt="'
        idx = buf.find( startalt )
        idx0 = buf.find( start ) # ensure it's not the alt of another image
        print("DBG: saveImageFromPage: idx: %d, idx0: %d" % (idx,idx0) )
        if idx0 > idx and idx != -1:
            buf = buf[idx+len(startalt):]
            idx2 = buf.find( '"' )
            alt = buf[:idx2]
            print("alt: '%s'" % alt)
        else:
            alt = ""
        
        fndest = os.path.basename(addr)
        fndest = fndest.split('?')[0]
        if alt != "":
            name,ext = os.path.splitext(fndest)
            fndest = name + "__alt_" + alt + ext
        fndest = dst + fndest
        print("Saving to '%s'" % fndest)
        orig = websiteorigin + addr
        nettools.download(orig,fndest)
        cpt += 1
        #~ break
    print("INF: saveImageFromPage: image found and saved: %s" % cpt )
# saveImageFromPage - end


example = "../alex_pytools/autotest_data/page_team_example.htm"
saveImageFromPage( example, websiteorigin = "http://anotherbrain.ai/")
