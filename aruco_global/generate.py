# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np
from cv2 import aruco # pip3 install opencv-contrib-python
from fpdf import FPDF # pip3 install fpdf

global_dictionnary_type = cv2.aruco.DICT_APRILTAG_36h10 # 6x6, 2320 codes
global_dictionnary_type = cv2.aruco.DICT_5X5_1000 # 5x5, 1000 codes

def rgba2rgb( rgba, background=(255,255,255) ):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros( (row, col, 3), dtype='float32' )
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background

    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B
    return rgb
# rgba2rgb - end

def computeStatOnArucoDict(aruco_dict):
    i = 0
    while 1:
        try:
            dummy = aruco_dict.get(i)
            dummy = aruco.drawMarker(aruco_dict,i, 20)
            i += 1
        except:
            nNbrMarkers = i
            break
            
    print("dictionnary markerSize: %s" % str(aruco_dict.markerSize) )
    print("dictionnary maxCorrectionBits: %s" % str(aruco_dict.maxCorrectionBits) )
    print("nNbrMarkers: %s" % nNbrMarkers )
# computeStatOnArucoDict - end

def generateImage( nNumMark, strName, strDstPath = "./generated/", strSrcPath = "./imgs/" ):
    try: os.makedirs( strDstPath )
    except: pass

    w=2100
    h=2970 # ~ A4 proportions
    
    white = 255,255,255
    grey = 127,127,127
    lgrey = 191,191,191
    llgrey = 223,223,223
    black = 0,0,0
    
    strImgIn = strSrcPath + strName + "."
    if os.path.exists(strImgIn+"png"):
        strImgIn += "png"
    else:
        strImgIn += "jpg"
        
    pic = cv2.imread(strImgIn,cv2.IMREAD_UNCHANGED) # also read potential alpha layer
    hp, wp, nNbrPlane = pic.shape
    if nNbrPlane == 4:
        # set white to pixel containing alpha at 0
        pic = rgba2rgb( pic, white )
        
    #~ BGRA[y,x,3]
    
    global global_dictionnary_type
    aruco_dict = aruco.Dictionary_get(global_dictionnary_type)
    #~ computeStatOnArucoDict(aruco_dict)

    aru = aruco.drawMarker(aruco_dict,nNumMark, 256)

    
    strImgOut = strDstPath + "card_" + strName + ".png"


    if 0:
        # reduce image to debug
        w//=4
        h//=4
    
    
    h_pic_dst = int(h/2.1) # define the final size of the pictures on the page
    w_pic_dst = (h_pic_dst * wp)//hp
    if w_pic_dst > w:
        w_pic_dst = int(w * 0.8)
        h_pic_dst = (w_pic_dst*hp)//wp
    
    xpic = (w-w_pic_dst)//2
    ypic = (h-h_pic_dst)//2
    
    w_aru = int(w/3.4) # 3.4 was fine, but seen from too much distance. /3.1 define the final size of the mark on the page
    h_aru = w_aru
    
    xaru = (w-w_aru)//2
    rAruMarginCoef = 0.036 # 0.015
    yaru = int(0+h*rAruMarginCoef)
    yaru2 = int(0+h*(1-rAruMarginCoef)-h_aru)
    
    im = np.zeros( (h,w,3), dtype=np.uint8 )
    im[:] = white
    
    pic = cv2.resize( pic, (w_pic_dst, h_pic_dst) )
    
    if 0:
        # turn mark to grey
        aru[:] //= 2
        aru[:] += 128
    aru = cv2.resize( aru, (w_aru, h_aru) )
    aru = cv2.cvtColor(aru,cv2.COLOR_GRAY2RGB)
    
    
    im[ypic:h_pic_dst+ypic,xpic:w_pic_dst+xpic]=pic[:]
    im[yaru:h_aru+yaru,xaru:w_aru+xaru]=aru[:]
    im[yaru2:h_aru+yaru2,xaru:w_aru+xaru]=aru[:]
    
    nMarginBorder = 70
    #~ cv2.putText(im, str(nNumMark), (nMarginBorder+20, int(h-nMarginBorder-20) ), cv2.FONT_HERSHEY_SIMPLEX, 1.4, black, 1)
    cv2.putText(im, str(nNumMark), (w-nMarginBorder-20-140, int(h-nMarginBorder-30) ), cv2.FONT_HERSHEY_SIMPLEX, 1.4, lgrey, 2 )
    
    if 1:
        nThickness = 44 # 30=> 3mm of plastic border after cut
        cv2.rectangle(im, (nThickness//2,nThickness//2),(w-1-nThickness//2,h-1-nThickness//2), llgrey, nThickness )

    if 1:
        # too bad redoing that for each image!!!
        logo = cv2.imread("logo_sbr.jpg")
        hl,wl,dummy = logo.shape
        wlf = 400
        hlf = (wlf*hl) // wl
        logo = cv2.resize( logo, (wlf,hlf) )
        nAddedMargin = 30
        #im[h-hlf-nMarginBorder-nAddedMargin:h-nMarginBorder-nAddedMargin,w-wlf-nMarginBorder-nAddedMargin:w-nMarginBorder-nAddedMargin] = logo
        im[h-hlf-nMarginBorder-nAddedMargin:h-nMarginBorder-nAddedMargin,nMarginBorder+nAddedMargin+10:nMarginBorder+nAddedMargin+wlf+10] = logo
    cv2.imwrite(strImgOut, im)

    if 0:
        im = cv2.resize( im, (w//4, h//4) )
        cv2.imshow("", im)
        cv2.waitKey(0)
    return strImgOut
# generateImage - end

def genereatePdfFromImages( listImgs, strOutPdfFilename, nOuputType=0 ):
    """
    Generate a pdf files from a list of images
    nRectoVersoHandling:
    - nOuputType: 0: print all NDEV
    """
    pdf = FPDF('P', 'mm', 'A4') # Portrait, measures in mm, format is A4
    #~ pdf.add_page()
    #~ pdf.set_font('Arial', 'B', 16)
    #~ pdf.cell(40, 10, 'Hello World!')
    #~ pdf.output(strOutPdfFilename, 'F')
    nImageW = 105
    nImageH = (nImageW*297)//210
    nNumImage = 0
    nNbrImagePerPage = 4
    bDoubleForVerso = True # prepare for being printed with verso corresponding to same image
    while 1:
        pdf.add_page()
        for i in range(nNbrImagePerPage):
            if nNumImage+i >= len(listImgs):
                break
            pdf.image(listImgs[nNumImage+i],x=int(nImageW*(i%2)), y=int(nImageH*(i//2)), w=nImageW)
        if bDoubleForVerso:
            pdf.add_page()
            for i in range(nNbrImagePerPage):
                if nNumImage+i >= len(listImgs):
                    break
                pdf.image(listImgs[nNumImage+i],x=int(nImageW*((i+1)%2)), y=int(nImageH*(i//2)), w=nImageW)
            
        nNumImage += nNbrImagePerPage
        
        if nNumImage >= len(listImgs):
            break
    print( "INF: genereatePdfFromImages: outputting to '%s'" % (strOutPdfFilename) )
    pdf.output( strOutPdfFilename, 'F' )
    
        
    

def generateFromCsv(strCsvFile):
    """
    generate all images and python datas from the global list as a csv
    - strCsvFile: global list as a csv
    """
    file = open(strCsvFile, "rt" )
    line = file.readline() # skip headers
    line = file.readline() # 2nd line
    nCpt = 0
    listFiles = []
    dictArucoDef = {} # store to generate a python library file
    while 1:
        line = file.readline()
        if len(line)<4:
            break
        print( "line: %s" % line )
        splitted = line.split(',')
        print( "splitted: %s" % splitted )
        strNumMark, strName, strCategory, strEnglish, strFrench = splitted[:5]
        if strName == '':
            continue
        nNumMark = int(strNumMark)
        strOutFilename = None
        strOutFilename = generateImage( nNumMark, strName )
        listFiles.append(strOutFilename)
        dictArucoDef[nNumMark] = [strEnglish, strFrench]
        nCpt += 1
        
        #~ if nCpt > 8:
            #~ break
    
    genereatePdfFromImages(listFiles, "generated.pdf")
    
    # generate python dictionnary files
    out = "# -*- coding: utf-8 -*-\n"
    out += "# generated files, don't modify!\n"
    out += "# tools are in abcdk/aruco_global_tools.py\n"
    out += "dictDesc = {\n"
    for k,d in sorted(dictArucoDef.items() ):
        out += "  %d: {'en': %s, 'fr': %s},\n" % (k,repr(d[0]),repr(d[1])) # ( (k,) + tuple(d) )
    out += "}\n"
    global global_dictionnary_type
    out += "nDictionaryType = %s" % global_dictionnary_type
    file = open("aruco_def.py", "wt" )
    file.write(out)
    file.close()
        
# generateFromCsv - end
        

# generateFromCsv - end    
generateFromCsv( "aruco_global_list - table1.csv" )