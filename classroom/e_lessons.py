#~ from fpdf import FPDF # pip3 install fpdf
import fitz # pip install PyMuPDF # https://pypi.org/project/PyMuPDF/#files
import cv2

def drawAndInteract( strLessonFilename = "lesson.pdf" ):
    if ".pdf" in strLessonFilename:
        doc = fitz.open(strLessonFilename)
        page = doc.loadPage(0) #number of page
        pix = page.getPixmap()
        output = "/tmp/outfile.png"
        pix.writePNG(output)
        strLessonFilename = output
        
    im = cv2.imread(strLessonFilename)    
    drawer = CV2_Drawer( im)
    while 1:
        if drawer.isFinished():
            break


drawAndInteract()