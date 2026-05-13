import cv2


def decodeQrCode(filename):
    try:
        img = cv2.imread(filename)
        #~ img = cv2.resize(img,(0,0),fx=0.2,fy=0.2)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(img)
        print("value: %s points: %s" % (value, points) )
        #~ print("straight_qrcode: %s" % (straight_qrcode) )
    except BaseException as err:
        print("ERR: decodeQrCode: %s" % str(err))
        
    cv2.imshow("img", img )
    cv2.waitKey(0)
    return
    


f = "C:/Users/alexa/AppData/Local/Google/AndroidStudio2022.2/device-explorer/samsung SM-A528B/sdcard/Download/almavision/image_1704652855331.jpg"

f = "c:/tmp/image_1704652855331_crop.jpg"
f = "c:/tmp/image_1704652855331_crop.jpg"
f = "c:/tmp/image_1704654074760.jpg"
decodeQrCode(f)

