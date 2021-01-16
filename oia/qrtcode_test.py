import cv2
import qrcode

# output file name
filename_qr_code = "qrcode.png"
#~ filename_qr_code = "photo_with_qrcode.jpg"

if 0:
    #generate an image containing a QR code
    # example data
    data = "Room: L206"

    # generate qr code
    img = qrcode.make(data)
    # save img to a file
    img.save(filename_qr_code)
    
if 0:
    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()

    if 1:
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


#~ img = cv2.imread(filename_qr_code)

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
        print("data: '%s', bbox:%s straight_qrcode:%s" % (data, bbox, straight_qrcode) )
        strPre = "Room: "
        if strPre in data:
            data = data[len(strPre):]
            print("Vous etes en %s" % data)
    cv2.imshow("qrcode",frame)
    #~ cv2.imshow('gray',gray)
    key = cv2.waitKey(100) & 0xFF
    if key == ord('q') or key == 27:
        break  




