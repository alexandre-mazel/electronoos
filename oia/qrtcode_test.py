# coding: cp1252
import cv2
import qrcode

def getDescription(name):
    d = {
            "L206": ("La salle 206", "Dans cette salle il y a pleins d'ordinateurs et un grand tableau blanc"),
            "Cantine": ("Le réfectoire", "Dans cette pièce, il y a pleins de tables et de chaise et Francoise qui fait le service, sur la droite vous trouverez des toilettes en cas d'urgences"),
        }
    try:
        return d[name]
    except BaseException as err:
        print("WRN: getDescription: key '%s' not found (err:%s)" % (name,str(err) ) )
    return "",""
        

def generateQRCode(data):
    #generate an image containing a QR code
    # example data
    data = "Room: L206"
    data = "Room: Cantine"
    filename_qr_code = data.replace(": ","__") + ".png"

    # generate qr code
    img = qrcode.make(data)
    # save img to a file
    img.save(filename_qr_code)
    
def findQRCodeInImage(filename):
    img = cv2.imread(filename)
    if img is None:
        print("ERR: file %s not found")
    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()

    if 0:
        # manual scan
        img = img[2100:2300,1050:1250]
        img = cv2.resize(img,None, fx=0.5,fy=0.5)
    if 1:
        # detect and decode
        data, bbox, straight_qrcode = detector.detectAndDecode(img)
        print("data: '%s', bbox:%s straight_qrcode:%s" % (data, bbox, straight_qrcode) )



    #~ img = cv2.resize(img,None, fx=0.25,fy=0.25)
    cv2.imshow("qrcode",img)
    cv2.waitKey(0)


def loopOnWebcam():
    cap = cv2.VideoCapture(1) #or 0 + cv2.CAP_DSHOW
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    detector = cv2.QRCodeDetector()
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        #~ print("ret: %s" % ret)
        if ret == False:
            time.sleep(0.3)
            continue
        data, bbox, straight_qrcode = detector.detectAndDecode(frame)
        # print("data: '%s', bbox:%s straight_qrcode:%s" % (data, bbox, straight_qrcode) )
        if data != "":
            #~ print("data: '%s', bbox:%s straight_qrcode:%s" % (data, bbox, straight_qrcode) )
            strPre = "Room: "
            if strPre in data:
                data = data[len(strPre):]
                print("Vous etes en %s" % data)
                name, desc = getDescription(data)
                print("Vous etes dans %s. %s" % (name,desc))
        cv2.imshow("qrcode",frame)
        #~ cv2.imshow('gray',gray)
        key = cv2.waitKey(100) & 0xFF
        if key == ord('q') or key == 27:
            break  
            
# loopOnWebcam - end


