import pptx # pip install python-pptx
import cv2

pres = pptx.Presentation()
blank_slide_layout = pres.slide_layouts[6]

aFiles = [
                "../data/fruit_face.jpg",
                "../data/face_bw5.jpg",
                "../data/inconnus.jpg",
            ]


for nNumPage, slideimgfilename in enumerate(aFiles):
    slideimg = cv2.imread(slideimgfilename)
    height,width = slideimg.shape[:2]

    # Set slide dimensions
    pres.slide_height = height * 9525
    pres.slide_width = width * 9525

    # Add slide
    slide = pres.slides.add_slide(blank_slide_layout)
    pic = slide.shapes.add_picture(slideimgfilename, 0, 0, width=width * 9525, height=height * 9525)

base_name = "generated"
print("Saving file: " + base_name + ".pptx")
pres.save(base_name + '.pptx')
print("Conversion complete. :)")
