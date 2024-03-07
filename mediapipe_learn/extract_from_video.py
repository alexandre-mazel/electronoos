import cv2
import mediapipe_fx
import mediapipe as mp

import time

def exportResult( PoseLandmarkerResult, file ):
    result = PoseLandmarkerResult.pose_landmarks
    for skel in result:
        s = ""
        for pt in skel:
            s += "[%s,%s,%s,%5.2f,%5.2f]," % (pt.x,pt.y,pt.z,pt.presence,pt.visibility)
        break
    print(s)
    file.write(s+"\n")


def extractFromVideo( strFilename, detector ):
    print( "INF: extractFromVideo: processing '%s'" % strFilename )
    nNumFrame = 0
    cap = cv2.VideoCapture( strFilename )
    # Check if camera opened successfully
    if not cap.isOpened():
      print("ERR: extractFromVideo: Error opening video file '%s'" % strFilename )
      return
      
    outfile = open(strFilename.replace(".mkv",".skl"),"wt")
 
    while(cap.isOpened()):
            
        ret, img = cap.read()
        if not ret:
            break
            
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        imagebuf = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        detection_result = detector.detect(imagebuf)
        print("detection_result:" + str(detection_result) );
        exportResult(detection_result,outfile)
        
        img[:] = (0,0,0)
        img2 = mediapipe_fx.draw_landmarks_on_image(img,detection_result)
        
        

        img2 = cv2.resize(img2,(0,0),fx=0.5,fy=0.5)
        cv2.imshow( 'detection',img2 )

        # Press ESC on keyboard to  exit
        key = cv2.waitKey(10)
        if key == 27:
            break
            
        nNumFrame += 1
           
    outfile.close()
    cap.release()
    cv2.destroyAllWindows()


detector = mediapipe_fx.init()
strPath = "C:/seq_vid2/sms/"
for f in os.listdir(strPath):
    if not ".mkv" in f:
        break
    extractFromVideo( strPath + f, detector)
