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
        # try many format:
        for template in ["%04d","%02d","%d","_%04d","_%02d","_%d"]:
            newname = filename + (template % n ) + file_extension
            print("INF: trying to open '%s'" % newname)
            if os.path.isfile(newname):
                print("INF: found '%s'" % newname)
                break
        if not os.path.isfile(newname):
            if n == 0:
                # sometimes, there's no zero...
                n += 1
                continue
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
    if len(sys.argv) < 2:
        print( "\nPdfToImgs\n\nSyntaxe: %s img_template pdf_file [L: Landscape]\n eg: %s im.png will create a pdf with im_0000.png, im_0001.png ..."  % (sys.argv[0],sys.argv[0]) )
        exit( 0 )
    strImgsTemplate = sys.argv[1]
    if len(sys.argv) > 2:
        strPdfFile = sys.argv[2]
    else:
        strPdfFile = sys.argv[1].replace(".jpg",".pdf").replace(".png",".pdf")
    
    bLandscape = False
    if len(sys.argv) > 3:
        bLandscape = sys.argv[3] == 'L'
        print("bLandscape: %s" % bLandscape )
    convertImgsToPdf( strImgsTemplate, strPdfFile, bLandscape = bLandscape )