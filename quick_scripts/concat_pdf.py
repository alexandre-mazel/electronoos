import cv2
import os

import fitz # pip install PyMuPDF # https://pypi.org/project/PyMuPDF/#files

def concatPdf( listPdfFilenameIn, strPdfFilenameOut ):
    out = fitz.Document()
    for f in listPdfFilenameIn:
        doc = fitz.open(f)
        #~ print("doc page number: %d" % (doc.pageCount) )
        #~ print("doc meta: %s" % (doc.metadata) )
        page = doc.loadPage(0)
        print( "page: (%s) %s" %(type(page), page ) )
        iml = doc.getPageImageList( 0, full=True )
        print( "iml: (%s) %s" %(type(iml), iml ) )
        if 0 or len(iml) !=1 :
            # insert page as if
            out.insertPDF(doc)
        else:
            # Recompress in jpg
            print("Page recompression...")
            rot = page.rotation
            print( "rot: (%s) %s" %(type(rot), rot ) )
            ref = iml[0][0]
            bbox = page.getImageBbox(iml[0])
            print( "bbox: (%s) %s" %(type(bbox), bbox ) )
            pixmap = fitz.Pixmap(doc,ref)
            pixmap.writePNG("/tmp/tmp.png")
            im = cv2.imread("/tmp/tmp.png")
            newpage=out.newPage()
            newpage.setMediaBox(bbox)
            if 0:
                #if newpage.number & 1:
                if rot == 90:
                    im=cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif rot == 270:
                    im=cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite("/tmp/tmp.jpg",im, [int(cv2.IMWRITE_JPEG_QUALITY), 40])

            newpage.setRotation(rot)
            newpage.insertImage(bbox, filename="/tmp/tmp.jpg", rotate =0)
            
    print("INF: writing to %s" % (strPdfFilenameOut) )
    out.save( strPdfFilenameOut, deflate=True )
    
def getBooksPdfChaptersName():
    astrListFile = []
    strPathIn = "C:/Users/amazel/Downloads/"
    for nNumChapter in range(1,20):
        for nNumPage in range(1,20):
            strFilename = "ch%d_%d.pdf" % (nNumChapter,nNumPage)
            if os.path.exists(strPathIn+strFilename):
                astrListFile.append(strPathIn+strFilename)
    return astrListFile
                
if __name__ == "__main__":
    strOut = "/tmp/generated.pdf"
    concatPdf(getBooksPdfChaptersName(), strOut )


