import cv2


def extractFromVideo( strFilename ):
    cap = cv2.VideoCapture( strFilename )
    # Check if camera opened successfully
    if not cap.isOpened():
      print("ERR: extractFromVideo: Error opening video file '%s'" % strFilename )
      return
 
    while(cap.isOpened()):
            
        ret, im = cap.read()
        if not ret:
            break

        im = cv2.resize(im,(0,0),fx=0.5,fy=0.5)
        cv2.imshow('Frame',im)

        # Press ESC on keyboard to  exit
        key = cv2.waitKey(10)
        if key == 27:
            break
              
    cap.release()
    cv2.destroyAllWindows()

    
extractFromVideo( "C:/seq_vid2/sms/sms_01.mkv")
