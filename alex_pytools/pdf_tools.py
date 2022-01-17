from fpdf import FPDF # pip3 install fpdf

def pdfMultiCell( pdf, x, y, txt, hInterlign, bCentered = False ):
    # please document !
    for line in txt.split('\n'):
        stw = pdf.get_string_width(line)
        if bCentered:
            xp = x - stw//2
        else:
            xp = x
        pdf.text(xp,y,line )
        y += hInterlign

def generatePdfFromImages( listImgs, strOutPdfFilename, strVersoText = None, nNbrImagePerPage = 1, aListArea = None, bAddPageNum = True ):
    """
    Generate a pdf files from a list of images
    - nNbrImagePerPage: currently tested: 1 and 4
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
    nNbrImageThisPage = 1000 # big value to force add a new page at first time
    bNewPage = 1
    while 1:
        print("image %d/%d" % (nNumImage,len(listImgs)) )
        if nNbrImageThisPage >= nNbrImagePerPage:
            pdf.add_page()
            nNbrImageThisPage = 0
            bNewPage = 1
        else:
            bNewPage = 0

        strFilename = listImgs[nNumImage]
        if 1:
            # potential convert 16b to 8b:
            import cv2
            import numpy as np
            im = cv2.imread(strFilename,cv2.IMREAD_ANYDEPTH)
            print(im.dtype)
            print(im.shape)
            if im.dtype == np.uint16:
                # convert to 8 bits
                print("INF: pdfMultiCell: converting on the fly to 8 bits" )
                im = cv2.imread(strFilename)
                tmpName = "/tmp/0000.png"
                cv2.imwrite(tmpName,im)
                strFilename = tmpName
        
        bDeleteCroppedImg = False
        if aListArea != None:
            im = cv2.imread(strFilename)
            r = aListArea[nIdxArea]
            im = im[r[1]:r[3],r[0]:r[2]]
            strFilename = "/tmp/crop%s.jpg" % str(time.time() )
            cv2.imwrite(strFilename, im, [int(cv2.IMWRITE_JPEG_QUALITY), 70]) #here you can change the quality!
            nIdxArea += 1
            if nIdxArea >= len(aListArea):
                nIdxArea = 0
                nNumImage += 1
            bDeleteCroppedImg = True
        else:
            nNumImage += 1
            
        yImage = int(nImageH*(nNbrImageThisPage//2))
        pdf.image(strFilename,x=int(nImageW*(nNbrImageThisPage%2)), y=yImage, w=nImageW)
        if bDeleteCroppedImg: os.remove(strFilename)
        
        nNbrImageThisPage += 1

            
        if bAddPageNum and bNewPage:
            pdf.set_font('Arial', '', 10)
            txt = "%d/%d" % (nNumImage,len(listImgs))
            hInterlign = 8
            x = nImageW//2 # centered
            x = nImageW-5 # right
            yPage = int(nImageH*((nNbrImagePerPage+1)//2))
            pdfMultiCell( pdf, x, yPage-2, txt, hInterlign, bCentered=True )
            
        if nNumImage >= len(listImgs):
            break
            
    # while - end
            
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

def test():
    for bNumPage in [False,True]:
        generatePdfFromImages(["../data/alexandre.jpg"], "temp_%s.pdf" % bNumPage,bAddPageNum=bNumPage)
        generatePdfFromImages(["../data/alexandre.jpg"]*4, "temp4_%s.pdf" % bNumPage,nNbrImagePerPage=4,bAddPageNum=bNumPage)

if __name__ == "__main__":
    test()
