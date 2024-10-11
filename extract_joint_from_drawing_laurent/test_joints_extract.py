import sys
sys.path.append("../mediapipe_learn/")

import mediapipe_fx

import mediapipe as mp
import cv2
import time

def extract_joint(filename):
    timeBegin = time.time()
    detector = mediapipe_fx.init()
    print("Init takes %.3fs" % (time.time()-timeBegin))
    img = cv2.imread(fn)
    print("img shape: %s" % str(img.shape))
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    imagebuf = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    
    detection_result = detector.detect(imagebuf)
    print("Detect takes %.3fs" % (time.time()-timeBegin))
    print("Detected: detected: %s" % detection_result )
    print("Detected: detected.segmentation_masks: %s" % detection_result.segmentation_masks )
    if detection_result.segmentation_masks == None:
        return False
    print("Detected: nbr shape: %s" % len(detection_result.segmentation_masks) )

    segmentation_mask = detection_result.segmentation_masks[0].numpy_view()
    #~ visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2)

    # STEP 5: Process the detection result. In this case, visualize it.
    if 1:
        timeBegin = time.time()
        annotated_image = mediapipe_fx.draw_landmarks_on_image(imagebuf.numpy_view(), detection_result)
        print("draw_landmarks_on_image takes %.3fs" % (time.time()-timeBegin))
        cv2.imshow("test2",cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
        cv2.imshow("mask",cv2.cvtColor(segmentation_mask, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)
    
    print("segmentation_mask[0][0]: %s" % segmentation_mask[0][0] )
    print("segmentation_mask[320][480]: %s" % segmentation_mask[320][480] )
    
    
    
fn = "../data/inconnus.jpg"
fn = "../test/girl-4051811_960_720.jpg"
#~ fn = "bonhomme_bleu.jpg"
fn = "bonhomme_bleu_crop.jpg"
#~ fn = "bonhomme_soleil.jpg"
extract_joint(fn)