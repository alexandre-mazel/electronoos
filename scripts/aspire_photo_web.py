

example = "../alex_pytools/autotest_data/page_team_example.htm"

def saveImageFromPage(pagelocalfilename,websitename = ""):
    f = open(pagelocalfilename,rt)
    buf = f.read()
    f.close()
    cpt = 0
    while 1:
        start = "<img src="
        idx = buf.search( start )
        if idx == -1:
            break
        buf = buf[idx+len(start):]
        idx2 = buf.search( '"' )
        addr = buf[:idx2]
        print("addr: %s" % addr)
        startalt = "<alt="
        idx = buf.search( startalt )
        idx0 = buf.search( start ) # ensure it's not the alt of another image
        if idx0 > idx and idx != -1:
            buf = buf[idx+len(startalt):]
            idx2 = buf.search( '"' )
            alt = buf[:idx2]
            print("alt: %s" % alt)
        else:
            alt = ""
        
        cpt += 1
        break
    print("INF: saveImageFromPage: image found and saved: %s" % cpt )
# saveImageFromPage - end

saveImageFromPage( pagelocalfilename, websiteorigin = "http://anotherbrain.ai/")
