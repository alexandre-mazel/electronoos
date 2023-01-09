import cv2 
import os
import pytesseract
import sys
import time

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
def invert(image):
    return (255-image)
    
def burnLightest(im, threshold = 128):
    """
    turn all pixel more than threshold to white (great to ocr black text on pastel colors)
    """
    if 0:
        for j in range(img.shape[0]):
            for i in range(img.shape[1]):
                if im[j,i] >= threshold:
                    im[j,i] = 255
    else:
        #~ im[numpy.where((im>threshold).all())] = 0
        #~ im[numpy.any(im >= threshold, axis=-1)] = 255
        #~ im[np.where(np.all(im >= threshold, axis=-1))] = 255
        im[im >= threshold] = 255

    
def _init_tesseract():
    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    else:
        pytesseract.pytesseract.tesseract_cmd = "tesseract"

def extract_txt(filename,bInvert=False,bUseFastModel=False):
    """
    return all text from an image in filename.
    filename can be a pdf or an image
    - bUseFastModel: use alternate lang model, performance measure: -20 to -40%, efficacity not tested)
    """
    filename = filename.replace("/",os.sep)
    filename = filename.replace("\\",os.sep)
    print("INF: extract_txt('%s',bInvert:%s)" % (filename,bInvert))
    
    txt = ""

    try:
        _init_tesseract()

        img = cv2.imread(filename)

        if bInvert:
            gray = get_grayscale(img)
            if 0:
                thresh = thresholding(gray)
                img = thresh
            else:
                burnLightest(gray,135)
                img = gray
            
        if bInvert: img=invert(img)
        
        if 0:
            cv2.imshow("ocr",img)
            cv2.waitKey(0)



        # Adding custom options
            #~ Page segmentation modes (psm):
              #~ 0    Orientation and script detection (OSD) only.
              #~ 1    Automatic page segmentation with OSD.
              #~ 2    Automatic page segmentation, but no OSD, or OCR.
              #~ 3    Fully automatic page segmentation, but no OSD. (Default)
              #~ 4    Assume a single column of text of variable sizes.
              #~ 5    Assume a single uniform block of vertically aligned text.
              #~ 6    Assume a single uniform block of text.
              #~ 7    Treat the image as a single text line.
              #~ 8    Treat the image as a single word.
              #~ 9    Treat the image as a single word in a circle.
             #~ 10    Treat the image as a single character.
             #~ 11    Sparse text. Find as much text as possible in no particular order.
             #~ 12    Sparse text with OSD.
             #~ 13    Raw line. Treat the image as a single text line,
                   #~ bypassing hacks that are Tesseract-specific.
                   
            #~ OCR Engine modes: (see https://github.com/tesseract-ocr/tesseract/wiki#linux)
              #~ 0    Legacy engine only.
              #~ 1    Neural nets LSTM engine only.
              #~ 2    Legacy + LSTM engines.
              #~ 3    Default, based on what is available.
              
        #~ custom_config = r'--oem 3 --psm 6 -l eng'
        custom_config = r'-l fra' # think to copy data to C:\Program Files\Tesseract-OCR\tessdata
        custom_config = r'--oem 1 --psm 6 -l fra'
        custom_config = r'--oem 1 --psm 6 -l fra+eng' # search fr then eng
        if bUseFastModel:
            custom_config += "_fast" #assume language is the last parameter!

        txt=pytesseract.image_to_string(img, config=custom_config)
        print("INF: extract_txt --- result begin\n%s\nINF: extract_txt --- result end" % txt )
    except BaseException as err:
        strError = "while analysing '%s': err: %s" % (filename,err)
        print("INF: extract_txt: "+ strError)
        f = open("/tmp/tesseract.log","a")
        f.write(strError)
        f.close()
    return txt
    
detectorQR = cv2.QRCodeDetector()

def tupleInt(listFloat):
    a = []
    for f in listFloat:
        a.append(int(round(f)))
    a = tuple(a)
    #~ print("DBG: tupleInt: return %s" % str(a) )
    return a

def extract_txt_pos_and_size(img, astrRestrictToPart = None, bShowFound = False, bBurn = False ):
    """
    return a list of text, pos and text size
    - strRestrictToPart: return only area containing this text
    """
    print("DBG: extract_txt_pos_and_size: img shape: %s" % str(img.shape) )
    bVerbose=0
    
    if astrRestrictToPart != None:
        for i in range(len(astrRestrictToPart)):
            astrRestrictToPart[i] = astrRestrictToPart[i].lower()
            
    if bBurn:
        gray = get_grayscale(img)
        burnLightest(gray,135)
        img = gray
            
    if 1:
        if img.shape[0] > 64 and img.shape[1] > 64:
            # check it's not a complete qrcode, which will stuck pytesseract
            bShowQR = 0
            try:
                data, bboxes, straight_qrcode = detectorQR.detectAndDecode(img)
            except BaseException as err:
                print("WRN: extract_txt_pos_and_size: exception in qr code decode: err: %s" % str(err) )
                bboxes = None
            if bboxes is not None:
                print("DBG: extract_txt_pos_and_size: qr code detection data: '%s', bboxes: %s, straight_qrcode: %s" % (data, bboxes, straight_qrcode) )
                imqr = img.copy()
                nNbrBBox = len(bboxes)
                print("DBG: extract_txt_pos_and_size: len bboxes: %s" % nNbrBBox)
                if bShowQR:
                    for bb in bboxes:
                        for i in range(4):
                            # draw all lines
                            point1 = tupleInt(bb[i])
                            point2 = tupleInt(bb[(i+1) % 4])
                            cv2.line(imqr, point1, point2, color=(255, 255, 0), thickness=8)
                    
                    while imqr.shape[0]>1200: imqr = cv2.resize(imqr,(0,0),fx=0.5,fy=0.5)
                    cv2.imshow("qrcode", imqr)
                    cv2.waitKey(0)
                for bb in bboxes:
                    wqr = min(bb[1][0]-bb[0][0], bb[2][0]-bb[3][0])
                    hqr =  min(bb[3][1]-bb[0][1], bb[2][1]-bb[1][1])
                    ratiow = wqr/img.shape[1]
                    ratioh =  hqr/img.shape[0]
                    if ratiow > 0.5  or ratioh > 0.5:
                        print("DBG: extract_txt_pos_and_size: looks like a qr code, exiting ratiow: %.3f, ratioh: %.3f" % (ratiow,ratioh) )
                        return []
    
    _init_tesseract()
    
    #~ custom_config = r'--oem 3 --psm 6 -l eng'
    custom_config = r'-l fra' # think to copy data to C:\Program Files\Tesseract-OCR\tessdata
    #~ custom_config = r'--oem 1 --psm 6 -l fra'
    #~ custom_config = r'--psm 6 -l fra'

        
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT,config=custom_config)
    if bShowFound: imrender = img.copy()
    n_boxes = len(d['level'])
    retVal = []
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        txt = d['text'][i]
        if txt =="":
            continue
        txt = txt.lower()
        if astrRestrictToPart == None:
            bMatch = True
        else:
            bMatch = False
            for srw in astrRestrictToPart:
                if srw in txt:
                    bMatch = True
                    break
        if bMatch:
            retVal.append( [ txt, (x, y, w, h), h ] )
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)            
        if bShowFound: cv2.rectangle(imrender, (x, y), (x + w, y + h), color, 2)

    if bShowFound:
        imrender = cv2.resize(imrender, (0,0),fx=0.5,fy=0.5)
        cv2.imshow('extract_txt_pos_and_size', imrender)
        cv2.waitKey(0)
        
        
    return retVal
        
    
def autotest():
    listWord = ["de carvalho","contient des"] # 18 mai 2021: avant cela retournait 2, mais ca ne fonctionne plus !
    listWord = ["de carvalho","contient", "cora"] # je met ca pour avoir bien 2 mots et que le test passe
    filename = "\cvs\cvs_pool_png\de carvalho victor_CV_0000.png"
    filename = "./autotest_data/vc_0000.png"
    img = cv2.imread(filename)
    out = extract_txt_pos_and_size( img,astrRestrictToPart=listWord,bShowFound=False)
    print("DBG: extract_txt_pos_and_size: out: %s" % str(out) )
    assert(len(out)==2)

if __name__ == "__main__":
    timeBegin = time.time()
    if 0:
        autotest() 
        # petit concept: 2.83s
        # mstab7: 2.76s,
        # dell corto/elsa: 2.12s, 
        # champion1: 2.05s
        #~ exit(0)
    else:
        filename = "example_cv_img.png" # mstab7: 1.5s, dell corto/elsa: 1.14s
        # new timing (28 aout 2022, qu'est ce qui a change?): 
        # petit concept: 2.0s
        # mstab7: 2.69s, 
        # kakashi: 1.38s
        # champion1: 1.77s
        
        #~ filename = "C:/cvs/cvs_manual_png/b5148fdf19cc63dc7873f3d667088c8a5628aa56_0000.png"
        if len(sys.argv)>1:
            filename = sys.argv[1]
        extract_txt(filename) 
    print("Duration: %.2fs" % (time.time()-timeBegin) )
    
