# based on 
# https://github.com/onnx/models/tree/main/vision/body_analysis/emotion_ferplus
# and 
# https://bleedai.com/facial-expression-recognition-emotion-recognition-with-opencv/
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import bleedfacedetector as fd # pip install bleedfacedetector
import time
 
# This is the magic command to show matplotlib graphs.
#~ %matplotlib inline


def init_emotion(model="models/emotion-ferplus-8.onnx"):
    
    timeBegin = time.time()
    
    # Set global variables
    global net,emotions
    
    # Define the emotions
    emotions = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Anger', 'Disgust', 'Fear', 'Contempt']
    
    # Initialize the DNN module
    net = cv2.dnn.readNetFromONNX(model)
    print( "INF: init_emotion: done in %.3fs" % ( time.time()-timeBegin) )
    
def getLibelleEmotion(idx):
    return emotions[idx]
    
def detectEmotion( image, bDebug = False ):
    """
    return a list of [face_pos, id emotion, confidence, libelle emotion]
    """
    
    if image is None:
        return None
    
    timeBegin = time.time()
    out = []
    
    # Make copy of  image
    img_copy = image.copy()
    
    # Detect faces in image
    faces = fd.ssd_detect(img_copy,conf=0.2)
    
    # Define padding for face ROI
    padding = 3
    
    # Iterate process for all detected faces
    for x,y,w,h in faces:
        if bDebug: print("DBG: detectEmotion: face found: %s" % str(x,y,w,h) ) 
        
        # Get the Face from image
        face = img_copy[y-padding:y+h+padding,x-padding:x+w+padding]
        
        # Convert the detected face from BGR to Gray scale
        gray = cv2.cvtColor(face,cv2.COLOR_BGR2GRAY)
        
        # Resize the gray scale image into 64x64
        resized_face = cv2.resize(gray, (64, 64))
        
        # Reshape the final image in required format of model
        processed_face = resized_face.reshape(1,1,64,64)
        
        # Input the processed image
        net.setInput(processed_face)
        
        # Forward pass
        Output = net.forward()
 
        # Compute softmax values for each sets of scores  
        expanded = np.exp(Output - np.max(Output))
        probablities =  expanded / expanded.sum()
        
        # Get the final probablities by getting rid of any extra dimensions 
        prob = np.squeeze(probablities)
        
        # Get the predicted emotion
        idxmax = prob.argmax()
        predicted_emotion = emotions[idxmax]
        rConf = prob[idxmax]
        out.append([(x,y,w,h),idxmax,rConf,predicted_emotion])
       
        if bDebug:
            # Write predicted emotion on image
            cv2.putText(img_copy,'{}'.format(predicted_emotion),(x,y+h+(1*20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 
                            2, cv2.LINE_AA)
            # Draw a rectangular box on the detected face
            cv2.rectangle(img_copy,(x,y),(x+w,y+h),(0,0,255),2)
    
    print("INF: detectEmotion: detected:\n%s" % str(out))
    if bDebug:
        # Display the image
        if 1:
            cv2.imshow("emotions",img_copy)
            cv2.waitKey(0)
        else:
            plt.figure(figsize=(10,10))
            plt.imshow(img_copy[:,:,::-1]);plt.axis("off");        

    duration = time.time()-timeBegin
    print("INF: detectEmotion takes %.3fs" % duration )
    return out
# detectEmotion - end
        
        
init_emotion()

def testDetect():
    bDebug = 1
    path_faces = "../../face_tools/faces/"
    listFiles = []
    #~ listFiles.append("../data/multiple_humans.jpg")
    #~ listFiles.append(path_faces+"frown/frown_0.jpg")
    #~ listFiles.append(path_faces+"frown/frown_e.jpg")
    listFiles.append(path_faces+"frown/frown_k.jpg")
    listFiles.append(path_faces+"frown/frown_q.jpg")
    listFiles.append(path_faces+"neutral/neutral_2.jpg")
    listFiles.append(path_faces+"neutral/neutral_j.jpg")
    listFiles.append(path_faces+"smile/smile_x1.jpg")
    listFiles.append(path_faces+"smile/smile_xk.jpg")
    

    for f in listFiles:
        print("\nINF: processing '%s'" % f )
        image = cv2.imread(f)
        res = detectEmotion(image,bDebug=bDebug)
        print("INF: res: %s" % str(res))    
    
    
if __name__ == "__main__":
    testDetect()
