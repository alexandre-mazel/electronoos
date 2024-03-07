# WRN: j'avais nammed ce fichier mediapipe.py et bien sur plus rien ne fonctionner :)

# cf https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python

# install lib:
# EduPython: outils/outils/pip
# install pip install mediapipe

# get datas from:
# http://cdn.pixabay.com/photo/2019/03/12/20/39/girl-4051811_960_720.jpg # a sauver en "girl.jpg"
# http://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task


import time

timeBegin = time.time()

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

print("Imports takes %.3fs" % (time.time()-timeBegin))

# if errors occurs:
# ImportError: cannot import name 'builder' from 'google.protobuf.internal' (C:\Python39\lib\site-packages\google\protobuf\internal\__init__.py)
# install the latest version (nowaday 4.25)
# pip install protobuf==3.19.6
# backup ...\site-packages\google\protobuf\internal\builder.py
# reinstall previous version (was 3.19.6)
# pip install protobuf==3.19.6
# copy builder.py in the current version ...\site-packages\google\protobuf\internal\




def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image
  


def init( strModelPath = "../models/" ):
    strModelFileName = "pose_landmarker_heavy.task"
    #~ strModelFileName = "pose_landmarker_full.task"
    #~ strModelFileName = "pose_landmarker_lite.task"
    
    strModelPathFileName = strModelPath + strModelFileName
    
    base_options = python.BaseOptions(model_asset_path=strModelPathFileName)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)
    return detector


def bokeh( detector, img ):
    """
    compute a bokeh on a filename
    return the computed image
    """
    # STEP 4: Detect pose landmarks from the input image.
    #~ detection_result = detector.detect(image)
    timeBegin = time.time()
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    imagebuf = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)

    detection_result = detector.detect(imagebuf)
    print("Detect takes %.3fs" % (time.time()-timeBegin))

    segmentation_mask = detection_result.segmentation_masks[0].numpy_view()
    #~ visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2)

    # STEP 5: Process the detection result. In this case, visualize it.
    if 1:
        timeBegin = time.time()
        annotated_image = draw_landmarks_on_image(imagebuf.numpy_view(), detection_result)
        print("draw_landmarks_on_image takes %.3fs" % (time.time()-timeBegin))
        cv2.imshow("test2",cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
        cv2.imshow("mask",cv2.cvtColor(segmentation_mask, cv2.COLOR_RGB2BGR))
    
    print("segmentation_mask[0][0]: %s" % segmentation_mask[0][0] )
    print("segmentation_mask[320][480]: %s" % segmentation_mask[320][480] )
    
    #~ return segmentation_mask
    
    imr = cv2.GaussianBlur(img,(9,9),cv2.BORDER_DEFAULT)
    print("shape imr: %s (%s)" % (str(imr.shape),imr.dtype))
    print("shape img: %s (%s)" % (str(img.shape),img.dtype))
    
    #~ img.copyTo(imr, segmentation_mask);
    print("shape seg: %s (%s)" % (str(segmentation_mask.shape),segmentation_mask.dtype))
    segmentation_mask = (segmentation_mask*255).astype(np.uint8)
    print("shape seg: %s (%s)" % (str(segmentation_mask.shape),segmentation_mask.dtype))
    
    # threshold on mask
    #~ ret,segmentation_mask = cv2.threshold(segmentation_mask, 200,255,cv2.THRESH_TOZERO)
    ret,segmentation_mask = cv2.threshold(segmentation_mask, 200,255,cv2.THRESH_BINARY)
    
    print("segmentation_mask[0][0]: %s" % segmentation_mask[0][0] )
    print("segmentation_mask[320][480]: %s" % segmentation_mask[320][480] )
    
    #~ mask = cv2.cvtColor(segmentation_mask,cv2.cv2.COLOR_BGR2GRAY)
    #~ print("shape mask: %s" % str(mask.shape))

    img_fg = cv2.bitwise_and(img, img, mask=segmentation_mask)
    #~ segmentation_mask_inv = segmentation_mask[:]
    segmentation_mask_inv = 255-segmentation_mask
    #~ segmentation_mask_inv = cv2.bitwise_not(segmentation_mask) # != 255-segmentation_mask
    print("shape seg inv: %s (%s)" % (str(segmentation_mask_inv.shape),segmentation_mask_inv.dtype))
    print("segmentation_mask[0][0]: %s" % segmentation_mask[0][0] )
    print("segmentation_mask[320][480]: %s" % segmentation_mask[320][480] )
    print("segmentation_mask_inv[0][0]: %s" % segmentation_mask_inv[0][0] )
    print("segmentation_mask_inv[320][480]: %s" % segmentation_mask_inv[320][480] )
    imr_bg = cv2.bitwise_and(imr, imr, mask=segmentation_mask_inv)
    imr = cv2.add(img_fg,imr_bg)
    #~ imr[segmentation_mask] = 0
    #~ return imr_bg
    #~ return img_fg
    
    if 1:
        # save all steps
        path = "/tmp/"
        cv2.imwrite(path+"mask.jpg", segmentation_mask)
        cv2.imwrite(path+"skel.jpg", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(path+"bg.jpg", imr_bg)
        cv2.imwrite(path+"fg.jpg", img_fg)
        cv2.imwrite(path+"res_bokeh.jpg", imr)
    return imr
 
 
def test():
    timeBegin = time.time()
    detector = init()
    print("Init takes %.3fs" % (time.time()-timeBegin))
    
    fn = "../test/girl-4051811_960_720.jpg"
    fn = "/tmp_frames/WIN_20240208_18_26_08_Pro-00116.jpg"

    img = cv2.imread(fn)
    imresult = bokeh(detector, img)

    cv2.imshow("orig",img)
    cv2.imshow("res",imresult)
    cv2.waitKey(0)
    
if __name__ == "__main__":
    test()

