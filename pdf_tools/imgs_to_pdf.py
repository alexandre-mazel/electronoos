import os
import sys
import pdf_to_pptx
if os.name == "nt":
    strElectroPath = "C:/Users/alexa/dev/git/electronoos/"
else:
    strElectroPath = os.path.expanduser("~/dev/git/electronoos/")
sys.path.append(strElectroPath+"/alex_pytools/")
import pdf_tools

def convertImgsToPdf(strStrSkull, strDestPdf,bLandscape=False ):
    # get all images
    imgs = []
    n = 0
    while 1:
        filename, file_extension = os.path.splitext(strStrSkull)
        newname = filename + ("%04d" % n ) + file_extension
        if not os.path.isfile(newname):
            break
        imgs.append(newname)
        n += 1
        
    if len(imgs) < 1:
        print("ERR: no image found with name starting from '%s'" % newname)
        return []
        
    #~ pdf_to_pptx.imagesToPres(imgs, pptx)
    print("INF: pasting to '%s' those images: %s" % (strDestPdf,imgs) )
        
    return pdf_tools.generatePdfFromImages(imgs,strDestPdf,bLandscape=bLandscape)


if __name__ == "__main__":
    #~ auto_test_im_to_pptx()
    #~ auto_test()
    #~ convertPdfToPpt("nda.pdf")
    
    strPdfFile = ""
    strDestFolder = None
    if len(sys.argv) < 3:
        print( "\nPdfToImgs\n\nSyntaxe: %s img_template pdf_file [L: Landscape]\n eg: %s im.png will create a pdf with im_0000.png, im_0001.png ..."  % (sys.argv[0],sys.argv[0]) )
        exit( 0 )
    strImgsTemplate = sys.argv[1]
    strPdfFile = sys.argv[2]
    
    bLandscape = False
    if len(sys.argv) > 3:
        bLandscape = sys.argv[3] == 'L'
        print("bLandscape: %s" % bLandscape )
    convertImgsToPdf( strImgsTemplate, strPdfFile, bLandscape = bLandscape )