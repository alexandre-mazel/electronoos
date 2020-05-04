#~ from fpdf import FPDF # pip3 install fpdf
import cv2
import time

import os
import sys
import time

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
#~ print("strLocalPath: " + strLocalPath)
if strLocalPath == "": strLocalPath = "./"
sys.path.append(strLocalPath+"/../alex_pytools/")
import draw_on_cv2

def drawAndInteract( strLessonFilename = "lesson.pdf" ):
    if ".pdf" in strLessonFilename:
        
        print("INF: drawAndInteract: loading pdf '%s'" % strLessonFilename )
        
        import fitz # pip install PyMuPDF # https://pypi.org/project/PyMuPDF/#files
        
        doc = fitz.open(strLessonFilename)
        #~ print("doc page number: %d" % (doc.pageCount) )
        #~ print("doc meta: %s" % (doc.metadata) )
        page = doc.loadPage(0) #number of page
        if 1:
            zoom_x = 2.0  # 2 => double resolution 72 dpi => 144
            zoom_y = 2.0  # vertical zoom
            mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
            pix = page.getPixmap(matrix = mat)
        else:
            pix = page.getPixmap()
        output = "/tmp/outfile.png"
        pix.writePNG(output)
        strLessonFilename = output
        doc.close()
        
    im = cv2.imread(strLessonFilename)
    
    # found each rect
    if 0:
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gray = (255-gray)
        (contours, hierarchy) = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print( "contours: %s" % str(contours) )
        print( "hierarchy: %s" % str(hierarchy) )
    
    drawer = draw_on_cv2.CV2_Drawable()
    drawer.create(im)
    drawer.setDrawColor((180,40,43))
    while 1:
        if drawer.isFinished():
            break
     
    print("writing last rendered!")
    cv2.imwrite( "/tmp/" + str(time.time()) + ".png", drawer.image )
    time.sleep(1.)


strLesson = "lesson.pdf"
#~ strLesson = "C:/Users/amazel/Downloads/2020-04-20_-_article_de_Le_Monde_remis_en_page_-_demographie_Paris_confinement_PDF.pdf"
strLesson = "C:/Users/amazel/Downloads/24_04.pdf"
strLesson = "C:/Users/amazel/Downloads/0504_4.pdf"
#~ strLesson = "/tmp/1587730327.8424518.png"
drawAndInteract(strLesson)