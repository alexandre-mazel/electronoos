# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np
from cv2 import aruco # pip3 install opencv-contrib-python
from fpdf import FPDF # pip3 install fpdf
import time


def pdfMultiCell( pdf, x, y, txt, hInterlign, bCentered = False ):
    for line in txt.split('\n'):
        stw = pdf.get_string_width(line)
        if bCentered:
            xp = x - stw//2
        else:
            xp = x
        pdf.text(xp,y,line )
        y += hInterlign

def generatePdfFromImagesAndText( listImgs, strOutPdfFilename, strVersoText = None, nNbrImagePerPage = 4, aListArea = None ):
    """
    Generate a pdf files from a list of images
    - aListArea: for each area one image will be generated and copied as a new image (one area per page if nbr_image_per_page = 1)
    """
    pdf = FPDF('P', 'mm', 'A4') # Portrait, measures in mm, format is A4
    #~ pdf.SetAuthor("amazel")
    #~ pdf.add_page()
    #~ pdf.set_font('Arial', 'B', 16)
    #~ pdf.cell(40, 10, 'Hello World!')
    #~ pdf.output(strOutPdfFilename, 'F')
    wA4 = 210
    hA4 = 297
    if nNbrImagePerPage > 1:
        nImageW = wA4/(nNbrImagePerPage//2)
    else:
        nImageW = wA4
    nImageH = (nImageW*hA4)//wA4
    nNumImage = 0
    bDoubleForVerso = False # prepare for being printed with verso corresponding to same image
    nIdxArea = 0
    nNbrImageThisPage = 1000
    while 1:
        print("image %d/%d" % (nNumImage,len(listImgs)) )
        if nNbrImageThisPage >= nNbrImagePerPage:
            pdf.add_page()
            nNbrImageThisPage = 0

        strFilename = listImgs[nNumImage]
        bDeleteImg = False
        if aListArea != None:
            im = cv2.imread(strFilename)
            r = aListArea[nIdxArea]
            im = im[r[1]:r[3],r[0]:r[2]]
            strFilename = "/tmp/crop%s.jpg" % str(time.time() )
            cv2.imwrite(strFilename, im, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            nIdxArea += 1
            if nIdxArea >= len(aListArea):
                nIdxArea = 0
                nNumImage += 1
            bDeleteImg = True
        else:
            nNumImage += 1
            
        pdf.image(strFilename,x=int(nImageW*(nNbrImageThisPage%2)), y=int(nImageH*(nNbrImageThisPage//2)), w=nImageW)
        if bDeleteImg: os.remove(strFilename)
        
        nNbrImageThisPage += 1
        
        if nNumImage >= len(listImgs):
            break
            
    if strVersoText != None:
        # add some text
        txt = strVersoText
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        #pdf.write(8, txt) # text as normal text
        #pdf.cell(0,8, txt, 1, 0, 'c') # not handling multiline
        # multi_cell to be tried
        nMarginTop = 25
        nMarginLeft = 0 # 10
        bCentered = True
        hInterlign = 8
        nCenter = 105
        x = 0
        if bCentered: x+=nCenter/2
        pdfMultiCell( pdf, x+nMarginLeft, 0+nMarginTop, txt, hInterlign, bCentered=bCentered )
        pdfMultiCell( pdf, x+nCenter+nMarginLeft, 0+nMarginTop, txt, hInterlign, bCentered=bCentered )
        pdfMultiCell( pdf, x+nMarginLeft, 148+nMarginTop, txt, hInterlign, bCentered=bCentered )
        pdfMultiCell( pdf, x+nCenter+nMarginLeft, 148+nMarginTop, txt, hInterlign, bCentered=bCentered )
    
    print( "INF: generatePdfFromImages: outputting to '%s'" % (strOutPdfFilename) )
    pdf.output( strOutPdfFilename, 'F' )
# generatePdfFromImagesAndText - end
    
def generateGaiaBirthday():
    fn = "C:/Users/amazel/perso/retouches/anniv_gaia_7_affiche copy.png"
    listImages = [fn]*4
    strVersoText = """
    Rejoins l'équipe des héroines:

    Dimanche 29 Mars 2020,
    de 14h30 à 18h30,
    au 12, Villa Candiotti.

    Tu peux venir avec tes
    supers pouvoirs!

    Confirme ta présence
    avant le 25 Mars,
    au 06.10.60.19.79
    """
    generatePdfFromImagesAndText(listImages, '/tmp/generated.pdf', strVersoText, nNbrImagePerPage = 4)
# generateGaiaBirthday - end

def generateSchoolBook():
    strSkul = "C:/Users/amazel/perso/manuel_scolaire/cp_je_lis_tome1__%03d.png"
    listImages = []
    aListArea = [(320,334,1344,1480),(1392,334,2386,1480)] # one area per page
    for nNumPage in range(500):
        strFileName = strSkul%nNumPage
        if os.path.isfile( strFileName ):
            listImages.append(strFileName)
            
        
    print("listImages: %s" % listImages )
    generatePdfFromImagesAndText(listImages, '/tmp/generated.pdf', nNbrImagePerPage = 1, aListArea=aListArea)
# generateSchoolBook - end

#~ generateGaiaBirthday()
generateSchoolBook()