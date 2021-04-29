import pptx # pip install python-pptx
import cv2

def imagesToPres( listFileImages, strDestFilenamePPT = "generated.pptx" ):
    pres = pptx.Presentation()
    blank_slide_layout = pres.slide_layouts[6]


    multiplier = 9525

    wmax,hmax = 1920,1080 # HD ratio
    wmax,hmax = 2100,2970 # A4

    if 0:
        # find maximum, based on images (interesing if many images have equivalent size)
        # else we will remains on a classic ratio
        for nNumPage, slideimgfilename in enumerate(listFileImages):
            slideimg = cv2.imread(slideimgfilename)
            height,width = slideimg.shape[:2]

            if width > wmax:
                wmax = width
                
            if height > hmax:
                hmax = height


    # Set slide dimensions
    pres.slide_width = wmax*multiplier
    pres.slide_height = hmax*multiplier

    for nNumPage, slideimgfilename in enumerate(listFileImages):
        slideimg = cv2.imread(slideimgfilename)
        height,width = slideimg.shape[:2]
        
        fit_w_h = int(wmax * height/width) # h when fitting w
        fit_h_w = int(hmax * width/height)
        # Cas 1: NoLose: on ne veut pas perdre des bouts d'images quitte a avoir du blanc sur les cotes
        # Cas 2: NoWhite: On ne veut pas avoir de blanc quitte a perdre un peu d'images
        bNoLose = 0 # else it's NoWhite
        if (bNoLose and fit_w_h > hmax) or (not bNoLose and fit_w_h < hmax):
            # on garde fit_h_w
            wnew, hnew = fit_h_w,hmax
        else:
            wnew, hnew = wmax,fit_w_h
        
        

        # Add slide
        slide = pres.slides.add_slide(blank_slide_layout)
        pic = slide.shapes.add_picture(slideimgfilename, multiplier*(wmax-wnew)/2, multiplier*(hmax-hnew)/2, width=wnew*multiplier, height=hnew*multiplier)

    base_name = "generated"
    print("INF: imagesToPres: Saving to file: " + strDestFilenamePPT )
    pres.save(strDestFilenamePPT)
# imagesToPres - end

def auto_test2():

    aFiles = [
                    "../data/fruit_face.jpg",
                    "../data/face_bw5.jpg",
                    "../data/inconnus.jpg",
                ]
                
    imagesToPres(aFiles)
    print("Conversion complete. :)")
    
def auto_test2():

    aFiles = [
                    "../data/fruit_face.jpg",
                    "../data/face_bw5.jpg",
                    "../data/inconnus.jpg",
                ]
                
    imagesToPres(aFiles)
    print("Conversion complete. :)")

if __name__ == "__main__":
    auto_test1()
    auto_test2()
    
