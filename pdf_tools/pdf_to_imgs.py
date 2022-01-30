import os
import sys
import pdf_to_pptx

def convertPdfToImgs(strSrcPdfFilename, strDestFolder = None ):
    if strDestFolder == None:
        path = os.path.normpath(strSrcPdfFilename)
        listFolder=path.split(os.sep)
        strDestFolder = os.sep.join(listFolder[:-1])
    if strDestFolder[-1] != os.sep: strDestFolder += os.sep
    
    print("INF: convertPdfToImgs: converting '%s' to folder '%s'" % (strSrcPdfFilename,strDestFolder) )

    listImgs = pdf_to_pptx.pdfToImages(strPdfFile, strDestFolder)
    print("INF: convertPdfToImgs: outputted: %s" % listImgs)
    return listImgs


if __name__ == "__main__":
    #~ auto_test_im_to_pptx()
    #~ auto_test()
    #~ convertPdfToPpt("nda.pdf")
    
    strPdfFile = ""
    strDestFolder = None
    if len(sys.argv) < 2:
        print( "\nPdfToImgs\n\nSyntaxe: %s <pdf filename> [dest folder]"  % sys.argv[0] )
        exit( 0 )
    strPdfFile = sys.argv[1]
    if len(sys.argv)>2:
        strDestFolder = sys.argv[2]
    convertPdfToImgs( strPdfFile, strDestFolder )