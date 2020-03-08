# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np
from cv2 import aruco # pip3 install opencv-contrib-python
from fpdf import FPDF # pip3 install fpdf


def pdfMultiCell( pdf, x, y, txt, hInterlign, bCentered = False ):
    for line in txt.split('\n'):
        stw = pdf.get_string_width(line)
        if bCentered:
            xp = x - stw//2
        else:
            xp = x
        pdf.text(xp,y,line )
        y += hInterlign

def genereatePdfFromImages( listImgs, strOutPdfFilename, nOuputType=0 ):
    """
    Generate a pdf files from a list of images
    nRectoVersoHandling:
    - 0: print all
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
    bDoubleForVerso = False # prepare for being printed with verso corresponding to same image
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
            
    # add some text
    txt = """
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
    
    print( "INF: genereatePdfFromImages: outputting to '%s'" % (strOutPdfFilename) )
    pdf.output( strOutPdfFilename, 'F' )
    
        
fn = "C:/Users/amazel/perso/retouches/anniv_gaia_7_affiche copy.png"
listImages = [fn]*4
genereatePdfFromImages(listImages, '/tmp/generated.pdf')