try:
    from fpdf import FPDF # pip3 install fpdf
    import fitz # pip install fitz PyMuPDF # https://pypi.org/project/PyMuPDF/#files # rpi: try first: sudo apt-get install mupdf libmupdf-dev
    # sur rpi: sudo apt-get install libxml2 python-lxml
except BaseException as err:
    print("WRN: pdf_tools: can't load library: %s" % str(err))
from copy import deepcopy
import os

def createEmptyPdf(filename,bSaveIt=True):
    """
    create an empty pdf, return the open document
    """
    doc = fitz.open()
    page = doc.new_page() # default is a4
    where = fitz.Point(50, 100)
    #~ page.insert_text(where, "PDF created with PyMuPDF", fontsize=50)
    print("INF: createEmptyPdf: writting to '%s'" % (filename) )
    if bSaveIt: doc.save(filename)
    return doc

class PdfMod:
    
    def __init__( self, src ):
        self.bVerbose=0
        self.load(src)
        
    def load( self, src ):
        if self.bVerbose: print("DBG: PdfMod.load: loading '%s'" % src )
        self.src = src # to know when saving if it's an update or a write (needed by the library)
        self.doc = fitz.open(src)
        self.page = self.doc[0]
        self.page.clean_contents() # remove all specific orientation and weird settings
        
        dict_ = self.page.get_text('dict')
        #~ self.page.Annot.clean_contents() 
        w = dict_["width"]
        h = dict_["height"]
        if self.bVerbose: print("DBG: PdfMod.load: page has w, h: %s, %s" % ( w, h ) )
        self.w = w
        self.h = h
        
        #~ rotation = self.page.rotation
        #~ self.page.set_rotation(1)
        
        # reset the crop box !!! (else, text are offsetter compare to rectangle drawing)
        cropbox = self.page.cropbox
        self.page.set_cropbox((0,0,w,h))

        
        if 0:
            print("*"*40)
            print("DBG: PdfMod.load: is_wrapped: %s" % self.page.is_wrapped )
            print("DBG: PdfMod.load: _dict_: %s" % dict_.keys() )
            block = dict_['blocks']
            print("blocks nbr: %d" % len(block))
            for b in block:
                print("block: %s" % b.keys() )
                print("   block: number: %s" % b['number'] )
                print("   block: type: %s" % b['type'] )
                print("   block: bbox: %s" % str(b['bbox']) )
                if b['type'] == 0:
                    print("   block: lines: %s" % str(b['lines']) )
        
    def addRect( self, rect, color = (1,1,1), bShadow=0, fillColor=None, transparency=0 ):
        rect = fitz.Rect( int(rect[0]*self.w), int(rect[1]*self.h), int(rect[2]*self.w), int(rect[3]*self.h) )
        

        if bShadow:
            rectShadow = deepcopy(rect)
            #~ print(dir(rectShadow))
            offx = 1
            offy = 1
            rectShadow.x0 += offx
            rectShadow.y0 += offy
            rectShadow.x1 += offx
            rectShadow.y1 += offy
            self.page.draw_rect(rectShadow,(0,0,0))
        
        self.page.draw_rect(rect,color,fill=fillColor,fill_opacity=1.-transparency)
        
    def addText( self, text, pos, fontsize, colorText = (1,1,1), bShadow=0 ):
        """
        pos: x, and y in ratio in page (0..1), from top of letter
        NB: sur certains cv les textes arrivent plus bas que les rectangle associees...
        """
        try:
            fontname = "Times-Roman"
            bContour = 0 # test de contour, mais beurk
            x,y = pos

            assert(0<= x <=1)
            assert(0<= y <=1)
            
            xtext = int(x*self.w)
            ytext = int(y*self.h)
            if self.bVerbose: print("xtext, ytext: %s, %s" % ( xtext, ytext ) )
            
            text_lenght = fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)
            
            rect = fitz.Rect( xtext, ytext, xtext+text_lenght+1, ytext+fontsize*1+1 )
            
            listoffsets = []
            fontsizeShadow = fontsize
            if  bShadow:
                listoffsets = [[1,1]]
            if bContour:
                # divers essais peu concluant:
                if 1:
                    listoffsets += [[1,0],[-1,0],[0,1],[0,-1]]
                    listoffsets += [[1,1],[-1,-1],[1,-1],[-1,1]]
                
                if 0:
                    listoffsets = [[-2,-1]]
                    fontsizeShadow = fontsize+2
                
            for offsets in listoffsets:
                offx,offy = offsets
                rectShadow = deepcopy(rect)
                #~ print(dir(rectShadow))
                offset = 1
                rectShadow.x0 += offx
                rectShadow.y0 += offy
                rectShadow.x1 += offx
                rectShadow.y1 += offy
                #
                #
                #
                # align:  0 = left, 1 = center, 2 = right, 3: justify
                rc = self.page.insert_textbox(rectShadow, text, fontsize = fontsizeShadow, fontname = fontname, fontfile = None, color=(0,0,0), align = 0)

            bUseTextBox = 0 # 1: ready for some alignement in the future
            
            #~ self.page.draw_rect(rect,colorText) # rect to debug
            
            y_offset_text = 0
            if bUseTextBox:
                y_offset_text -= 10 # textbox render everything lower
                rc = self.page.insert_textbox(rect, text, fontsize = fontsize, # choose fontsize (float)
                                   fontname = fontname,       # a PDF standard font: "Times-Roman"
                                   fontfile = None,                # could be a file on your system
                                   color=colorText,
                                   #~ border_width=3,
                                   align=0)                      # 0 = left, 1 = center, 2 = right;
            else:
                y_offset_text += fontsize # origin is from the bottom left corner
                rc = self.page.insert_text((rect[0],rect[1]+y_offset_text), text, fontsize = fontsize, # choose fontsize (float)
                                   fontname = fontname,       # a PDF standard font: "Times-Roman"
                                   fontfile = None,                # could be a file on your system
                                   color=colorText,
                                   #~ border_width=3,
                                   )                      # 0 = left, 1 = center, 2 = right;
            if self.bVerbose: print("rc: %s" % str(rc))
        except ValueError as err:
            # got a bug with 1cef88666bef8f9cbf8e5525d1746a866905b2ed.pdf when cartelling:
            # error: xref is not a font
            print("ERR: PdfMod.addText: looks like a random error: %s" % str(err))
        
    def save( self, dst ):
        print("INF: PdfMod: saving to '%s'" % dst )
        if 0:
            # using increment save, (but doesn't work on a repaired file...)
            self.doc.save(dst,incremental=self.src==dst,encryption=fitz.PDF_ENCRYPT_KEEP)
        if self.src != dst:
            self.doc.save(dst,encryption=fitz.PDF_ENCRYPT_KEEP)
        else:
            dst_temp = dst.replace(".pdf", "_temp.pdf")
            self.doc.save(dst_temp,encryption=fitz.PDF_ENCRYPT_KEEP)
            self.doc = None
            os.unlink(dst)
            os.rename(dst_temp,dst)
            self.load(dst) # optionnal, just to keep the object ready to next modification
        
# class PdfMod

def testPdfMod():
    files = []
    files.append(("cv_sample.pdf", "temp.pdf")) # cv with some offset when rendering
    files.append(("cv_sample2.pdf", "temp2.pdf")) # cv ok
    for src,dst in files:
        p = PdfMod(src)
        colorRect = (0.5,0.5,0.5)
        xo = 0.75
        sizetxt=10
        p.addRect( (xo-0.01,0.0,1.,0.05),color=colorRect, fillColor=colorRect, transparency=0.07 )
        p.addText( "luxe: 0.4", (xo,0.), sizetxt, colorText = (0,0,0) )
        p.addText( "premium: 0.4 (Kenzo, kookai,...)", (xo,0.015), sizetxt, colorText = (0,0,0) )
        p.addText( "dist: 18km (75000)", (xo,0.03), sizetxt, colorText = (0,0,0) )
        p.save(dst)

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

def generatePdfFromImages( listImgs, strOutPdfFilename, strVersoText = None, nNbrImagePerPage = 1, aListArea = None, bAddPageNum = True, bLandscape = False ):
    """
    Generate a pdf files from a list of images
    - nNbrImagePerPage: currently tested: 1 and 4
    - aListArea: for each area one image will be generated and copied as a new image (one area per page if nbr_image_per_page = 1)
    """
    if bLandscape:
        pdf = FPDF('L', 'mm', 'A4') # Portrait, measures in mm, format is A4
    else:
        pdf = FPDF('P', 'mm', 'A4') # Portrait, measures in mm, format is A4
    #~ pdf.SetAuthor("amazel")
    #~ pdf.add_page()
    #~ pdf.set_font('Arial', 'B', 16)
    #~ pdf.cell(40, 10, 'Hello World!')
    #~ pdf.output(strOutPdfFilename, 'F')
    wA4 = 210
    hA4 = 297
    
    if bLandscape:
        wA4 = hA4
        hA4 = 210
        
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
            if im is None:
                print( "ERR: generatePdfFromImages: image can't be loaded: %s" % strFilename ) 
                nNumImage += 1
                if nNumImage >= len(listImgs):
                    break
                continue
            print("DBG: pdfMultiCell: im.dtype: %s" % str(im.dtype))
            print("DBG: pdfMultiCell: im.shape: %s" % str(im.shape))
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


def pdf_full_page_to_img(src,dst):
    """
    convert each page of a pdf to an img.
    output image only in png
    return the list of created image
    """
    print("INF: pdf_full_page_to_img: '%s' => '%s'" % (src,dst))
    
    if os.path.isfile(dst.replace(".png","_%04d.png"%0)):
        # already existing, let's just return the filename
        listImg = []
        nNumPage = 0
        while os.path.isfile(dst.replace(".png","_%04d.png"%nNumPage)):
            listImg.append(dst.replace(".png","_%04d.png"%nNumPage))
            nNumPage += 1
        return listImg
    
    print("INF: pdf_full_page_to_img: really generating images" )
    """
    # require poppler :(
    import pdf2image 
    pages = pdf2image.convert_from_path(src, 500)

    nNumPage = 1
    for page in pages:
        page.save(dst.replace(".jpg","%04d.jpg"%nNumPage), 'JPEG')
        nNumPage += 1
    """
    
    listImg = []
    # python -m pip install --upgrade pip
    import fitz # python -m pip install --upgrade pymupdf
    doc = fitz.open(src)
    bFitz16=False
    try:
        nbrPage = doc.page_count
    except:
        # old fitz version
        bFitz16 = True
        nbrPage = doc.pageCount
        doc.load_page=doc.loadPage
    for i in range(nbrPage):        
        print("INF: pdf_full_page_to_img: converting page %d" % i )
        page = doc.load_page(i)  # number of page
        if not hasattr(page,"get_pixmap"):
                page.get_pixmap=page.getPixmap
        # zoom not working
        #~ zoom = 2    # zoom factor
        #~ mat = fitz.Matrix(zoom, zoom)
        #~ pix = page.get_pixmap(matrix=map)
        dpiList = [300,150,75]
        pageBound = page.bound()
        print("DBG: pdf_full_page_to_img: page.bound: %s" % str(pageBound))
        if pageBound[2]-pageBound[0]>7500 or pageBound[3]-pageBound[1]>7500:
            print("DBG: pdf_full_page_to_img: reducing dpi...(1)")
            dpiList = [50,25]
        elif pageBound[2]-pageBound[0]>4000 or pageBound[3]-pageBound[1]>4000:
            print("DBG: pdf_full_page_to_img: reducing dpi... (2)")
            dpiList = [150,75]
        for dpi in dpiList:
            try:
                if bFitz16: 
                    pix = page.get_pixmap()
                    #~ print(dir(pix))
                    pix.save = pix.writeImage
                else: 
                    pix = page.get_pixmap(dpi=dpi)
                output = dst.replace(".png","_%04d.png"%i)
                pix.save(output)
                print("DBG: pix.size: %sx%s" % (str(pix.width),str(pix.height)))
                listImg.append(output)
                break; # exit of the for dpi
            except BaseException as err:
                print("WRN: pdf_full_page_to_img: err occurs, trying with smaller def (dpi:%d), err: %s" % (dpi, err))
                if "such file or directory" in str(err):
                    print("\n"*5)
                    print("ERR: Tu dois enlever et remettre la carte sur d:")
                    print("waiting...")
                    import misctools
                    import time
                    misctools.beepError(4)
                    time.sleep(10)
    return listImg

if __name__ == "__main__":
    pass
    #~ test()
    testPdfMod()
    
