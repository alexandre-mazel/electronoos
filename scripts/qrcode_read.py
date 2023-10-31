import cv2

def decodeQrCode(filename):
    try:
        img = cv2.imread(filename)
        #~ img = cv2.resize(img,(0,0),fx=0.2,fy=0.2)
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(img)
        print("value: %s points: %s straight_qrcode: %s" % (value, points, straight_qrcode) )
    except BaseException as err:
        print("ERR: decodeQrCode: %s" % str(err))
        
    cv2.imshow("img", img )
    cv2.waitKey(0)
    return
    
    
filename = "./test/qrcode_reseau.jpg" # ne fonctionne pas sur ce code!
decodeQrCode(filename)

