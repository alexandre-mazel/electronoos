import os

import fitz # pip install PyMuPDF # https://pypi.org/project/PyMuPDF/#files

def concatPdf( listPdfFilenameIn, strPdfFilenameOut ):
    out = fitz.Document()
    for f in listPdfFilenameIn:
        doc = fitz.open(strLessonFilename)
        #~ print("doc page number: %d" % (doc.pageCount) )
        #~ print("doc meta: %s" % (doc.metadata) )
        page = doc.loadPage(0) #number of page
        out.insertPage(page)
    out.save( strPdfFilenameOut )
    
def getBooksPdfChaptersName():
    astrListFile = []
    strPathIn = "C:/Users/amazel/Downloads/"
    for nNumChapter in range(1,20):
        for nNumPage in range(1,20):
            strFilename = "ch%d_%d.pdf" % (nNumChapter,nNumPage)
            if os.path.fileexists(strPathIn+strFilename):
                astrListFile.append(strPathIn+strFilename)
    return astrListFile
                
if __name__ == "__main__":
    strOut = "/tmp/generated.pdf"
    concatPdf(getBooksPdfChaptersName(), strOut )


