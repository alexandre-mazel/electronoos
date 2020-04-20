#~ from fpdf import FPDF # pip3 install fpdf
import fitz # pip install PyMuPDF # https://pypi.org/project/PyMuPDF/#files
import cv2

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
#~ print("strLocalPath: " + strLocalPath)
if strLocalPath == "": strLocalPath = "./"
sys.path.append(strLocalPath+"/../alex_pytools/")
import draw_on_cv2

def drawAndInteract( strLessonFilename = "lesson.pdf" ):
    if ".pdf" in strLessonFilename:
        doc = fitz.open(strLessonFilename)
        page = doc.loadPage(0) #number of page
        pix = page.getPixmap()
        output = "/tmp/outfile.png"
        pix.writePNG(output)
        strLessonFilename = output
        
    im = cv2.imread(strLessonFilename)
    
    # found each rect
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gray = (255-gray)
    (contours, hierarchy) = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print( "contours: %s" % str(contours) )
    print( "hierarchy: %s" % str(hierarchy) )
    
    drawer = draw_on_cv2.CV2_Drawer( im )
    while 1:
        if drawer.isFinished():
            break


drawAndInteract()