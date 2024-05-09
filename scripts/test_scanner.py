import win32com.client, time, os

WIA_COM = "WIA.CommonDialog"

#~ WIA_DEVICE_UNSPECIFIED = 0
#~ WIA_DEVICE_CAMERA = 2

#~ WIA_INTENT_UNSPECIFIED = 0

#~ WIA_BIAS_MIN_SIZE = 65536
#~ WIA_BIAS_MAX_QUALITY = 65536

#~ WIA_COMMAND_TAKE_PICTURE="{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"

WIA_IMG_FORMAT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"


def acquire_image_wia(strDstFilename,rectToScan=(0,0,210,297),nBitsPerPixel=24,nResolution = 300):
    """
    scan an image and save it to disk
    - strDstFilename: pathfilenale of destination
    - rectToScan: rect to grab in milimeters (default: A4)
    - nBitsPerPixel: 1: N&B, 8: gray, 24: color
    - nResolution: resolution in DPI (300, 600, ...)
    """
    wia = win32com.client.Dispatch(WIA_COM) # wia is a CommonDialog object
    dev = wia.ShowSelectDevice()
    scanner = dev.Items[0]
    
    rMagicCoef =  1.17 # looks like a magic, tuned for my canon lide 70. perhaps some DotToInch explanations...
    
    r = []
    for x in rectToScan:
        r.append(int(x*10*rMagicCoef*nResolution/300))
        
    for p in scanner.Properties:
        if p.Name == "Horizontal Start Position":
            p.value = r[0]
        if p.Name == "Vertical Start Position":
            p.value = r[1]
        if p.Name == "Horizontal Extent":
            p.value = r[2]
        if p.Name == "Vertical Extent":
            p.value = r[3]
        if p.Name == "Bits Per Pixel":
            p.value = nBitsPerPixel
        if p.Name == "Horizontal Resolution":
            p.value = nResolution
        if p.Name == "Vertical Resolution":
            p.value = nResolution
            
    image=scanner.Transfer(WIA_IMG_FORMAT_PNG)

    if os.path.exists(strDstFilename):
        os.remove(strDstFilename)
    image.SaveFile(strDstFilename)


def acquire_image_wia_test():
    wia = win32com.client.Dispatch(WIA_COM) # wia is a CommonDialog object
    dev = wia.ShowSelectDevice()
    for command in dev.Commands:
        if command.CommandID==WIA_COMMAND_TAKE_PICTURE:
            foo=dev.ExecuteCommand(WIA_COMMAND_TAKE_PICTURE)

    item = dev.Items[0]
    for p in item.Properties:
        if not p.IsReadOnly:
            print( "%s: %s" % (p.Name,  p.Value) )
            # all those are working !
            #~ if p.Name == "Vertical Extent":
                #~ p.value = 2000 #change len to scan
            if p.Name == "Bits Per Pixel":
                p.value = 8 #gray
            if p.Name == "Bits Per Pixel":
                p.value = 24 #RGB
            #~ if p.Name == "Horizontal Resolution":
                #~ p.value = 600
            #~ if p.Name == "Vertical Resolution":
                #~ p.value = 600
    #~ i=1
    #~ for item in dev.Items:
        #~ if i==dev.Items.Count:
            #~ image=item.Transfer(WIA_IMG_FORMAT_PNG)
            #~ break
        #~ i=i+1
        
    image=item.Transfer(WIA_IMG_FORMAT_PNG)

    fname = 'wia-test.png'
    if os.path.exists(fname):
        os.remove(fname)
    image.SaveFile(fname)
    
def countTrigramme(txt):
    # count "trigramme", as part of word classical # du pauvre car fait "vite fait"
    listTri = ["thi","tha","ce", "com", "est", "sig", "tit", "en", "pren", "par", "ti", "je", "tu", "il", "nous", "vous", "ils", "page", "for", "le", "la", "un", "de", "du", "de le", "de la", "mon", "ton", "son", "aux", "a","car","alex"]
    txt = txt.lower()
    words = txt.split()
    n = 0
    for w in words:
        if w in listTri:
            n += 1
    return n
    
    
def preprocessExportedFile(filename):
    """
    return name of the new created preprocessed file
    """
    import sys
    sys.path.append("../alex_pytools/")
    import ocr_tools
    import cv2
    import cv2_tools
    im = cv2.imread(filename)
    im = cv2_tools.autoCrop(im,bDebug=1)
    
    bf,ext = os.path.splitext(filename)
    ext = ".jpg"
    filename_dst = bf + "_pp" + ext
    cv2.imwrite(filename_dst,im)
    im2 = cv2.flip(im, -1)
    filename_dst2 = bf + "_ppf" + ext
    cv2.imwrite(filename_dst2,im2)
    #~ exit(1)
    
    txt1=ocr_tools.extract_txt(filename_dst)
    print("")
    print("ocr1 (len:%s):" % len(txt1))
    print(txt1)
    
    txt2=ocr_tools.extract_txt(filename_dst2)
    print("")
    print("ocr2 (len:%s):" % len(txt2))
    print(txt2)
    
    # on elsa passport: 2189 contre 2137 pour la version flipped qui est pourtant la bonne !
    #~ bRotIsBetter = len(txt2) > len(txt1)
    
    tri1 = countTrigramme(txt1)
    tri2 = countTrigramme(txt2)
    print("tri1: %s" % tri1 )
    print("tri2: %s" % tri2 )
    bRotIsBetter = tri2 > tri1
    if bRotIsBetter:
        filename_to_delete = filename_dst
        filename_dst = filename_dst2
    else:
        filename_to_delete = filename_dst2
    os.unlink(filename_to_delete)
    
    print("INF: preprocessExportedFile: cleaned file exported to '%s'" % filename_dst )
    return filename_dst

def testLoopBugMyScanner():
    os.chdir("c:/tmp")
    while 1:
        try:
            acquire_image_wia_test()
            break
        except BaseException as err:
            print("err: %s" % err)
           
       
def runManyTimes( nNbrTimes = 50 ):
    for i in range(nNbrTimes):
        try:
            acquire_image_wia("c:/tmp/wia-test2.png",nResolution=300)
            print("INF: Success!")
            break
        except BaseException as err:
            print("ERR: try %d: %s" % (i,err))
            
#~ runManyTimes()   
#~ preprocessExportedFile("c:/tmp/wia-test2a.png")
preprocessExportedFile("../data/wia-test2a.png")
preprocessExportedFile("../data/wia-test2b.png")

