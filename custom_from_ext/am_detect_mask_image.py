# USAGE
# python detect_mask_image.py --image examples/example_01.png
import cv2 # for jetson: import cv2 before tensorflow
# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os
import time

class MaskDetector:
    
    def __init__( self ):
        pass
        
    def loadModels( self, strFaceDetectorModel, strFaceDetectorWeights, strMaskClassificationModel ):
        print("INF: MaskDetector.loadModels: loading models..." )
        
        # load our serialized face detector model from disk
        print("INF: loading face detector model...")
        self.faceDetectNet = cv2.dnn.readNet(strFaceDetectorModel, strFaceDetectorWeights)

        # load the face mask detector model from disk
        print("INF: loading mask detector model...")
        self.MaskDetectModel = load_model( strMaskClassificationModel )
        
        # preload everything
        self.detectFromImage(np.zeros((128,128,3), np.uint8), bShowResults = False )
        
        print("INF: MaskDetector.loadModels: end..." )

    def detectFromImageFile( self, strFilename, bShowResults = True ):
        im = cv2.imread( strFilename )
        return self.detectFromImage( im, bShowResults=bShowResults )
        
    def detectFromImage( self, image, bShowResults = True ):
        orig = image.copy()
        (h, w) = image.shape[:2]

        print("INF: starting on image")

        # construct a blob from the image
        timeBegin = time.time()
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
            (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        print("[INFO] computing face detections...")
        self.faceDetectNet.setInput(blob)
        detections = self.faceDetectNet.forward()

        print("INF: face detect: %5.2fs" % (time.time()-timeBegin) ) # 0.09s mode2: 0.21s

        nCptFace = 0
        
        print("INF: nbr detected shape: %s" % str(detections.shape[2]) )
        
        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the detection
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # compute the (x, y)-coordinates of the bounding box for
                # the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # ensure the bounding boxes fall within the dimensions of
                # the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                # extract the face ROI, convert it from BGR to RGB channel
                # ordering, resize it to 224x224, and preprocess it
                face = image[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)
                face = np.expand_dims(face, axis=0)

                # pass the face through the model to determine if the face
                # has a mask or not
                timeBegin = time.time()
                (mask, withoutMask) = self.MaskDetectModel.predict(face)[0]
                print("INF: predictions: %s %5.2fs" % (str((mask, withoutMask)), time.time()-timeBegin) ) # 0.04s / mode2: 0.07
                
                nCptFace += 1

                if bShowResults:
                    # determine the class label and color we'll use to draw
                    # the bounding box and text
                    label = "Mask" if mask > withoutMask else "No Mask"
                    color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                    # include the probability in the label
                    label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                    # display the label and bounding box rectangle on the output
                    # frame
                    cv2.putText(image, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

        print("INF: nbr detected faces: %s" % str(nCptFace) )
        
        if bShowResults:
            # show the output image
            cv2.imshow("Output", image)
            cv2.waitKey(0)
        
    # detectFromImage - end

# class MaskDetector - end			

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-f", "--face", type=str,
	default="face_detector",
	help="path to face detector model directory")
ap.add_argument("-m", "--model", type=str,
	default="mask_detector.model",
	help="path to trained face mask detector model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

totalScriptTimeBegin = time.time()

md = MaskDetector()

prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
weightsPath = os.path.sep.join([args["face"], "res10_300x300_ssd_iter_140000.caffemodel"])		
md.loadModels( prototxtPath, weightsPath, args["model"] )



# load the input image from disk, clone it, and grab the image spatial
# dimensions
md.detectFromImageFile(args["image"], bShowResults = False)

print( "INF: measuring time..." )
timeBegin = time.time()
md.detectFromImageFile(args["image"], bShowResults = False)
print("INF: Total time: %5.3fs" % (time.time()-timeBegin) )
print("INF: Total Script time: %5.2fs" % (time.time()-totalScriptTimeBegin) )
