# WRN: j'avais nammed ce fichier mediapipe.py et bien sur plus rien ne fonctionner :)

# cf https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python

# install lib:
# EduPython: outils/outils/pip
# install pip install mediapipe

# get datas from:
# http://cdn.pixabay.com/photo/2019/03/12/20/39/girl-4051811_960_720.jpg # a sauver en "girl.jpg"
# http://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task


from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
    strModelFileName = "pose_landmarker_full.task"
    strModelFileName = "pose_landmarker_lite.task"
    
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

    # STEP 5: Process the detection result. In this case, visualize it.
    timeBegin = time.time()
    annotated_image = draw_landmarks_on_image(imagebuf.numpy_view(), detection_result)
    print("draw_landmarks_on_image takes %.3fs" % (time.time()-timeBegin))
    cv2.imshow("test2",cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    


    segmentation_mask = detection_result.segmentation_masks[0].numpy_view()
    visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2) * 255
    return visualized_mask
 
 
def test():
    timeBegin = time.time()
    detector = init()
    print("Init takes %.3fs" % (time.time()-timeBegin))
    
    fn = "../test/girl-4051811_960_720.jpg"

    img = cv2.imread(fn)
    imresult = bokeh(detector, img)

    cv2.imshow("orig",img)
    cv2.imshow("res",imresult)
    cv2.waitKey(0)
    


test()

