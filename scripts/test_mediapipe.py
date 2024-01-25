# lien framapad:
# https://mensuel.framapad.org/p/dbhhf3tied-a5p4

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
  
  
model_path = "../models/pose_landmarker_heavy.task"
#~ model_path = "../models/pose_landmarker_full.task"
#~ model_path = "../models/pose_landmarker_lite.task"

# mstab7:
# lite: 0.040s # second 0.030
# full: 0.050s # second 0.035
# heavy: 0.087s # second 0.070

def test():
    fn = "../test/girl-4051811_960_720.jpg"

    import cv2
    #~ from google.colab.patches import cv2_imshow

    img = cv2.imread(fn)
    #~ cv2_imshow(img)
    cv2.imshow("test",img)
    cv2.waitKey(100)
    


    # STEP 1: Import the necessary modules.
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    # STEP 2: Create an PoseLandmarker object.
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)

    # STEP 3: Load the input image.
    image = mp.Image.create_from_file(fn)

    # STEP 4: Detect pose landmarks from the input image.
    #~ detection_result = detector.detect(image)
    timeBegin = time.time()
    detection_result = detector.detect(image)
    print("Detect takes %.3fs" % (time.time()-timeBegin))

    # STEP 5: Process the detection result. In this case, visualize it.
    timeBegin = time.time()
    annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
    print("draw_landmarks_on_image takes %.3fs" % (time.time()-timeBegin))
    cv2.imshow("test2",cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    


    segmentation_mask = detection_result.segmentation_masks[0].numpy_view()
    visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2) * 255
    cv2.imshow("mask",visualized_mask)
    cv2.waitKey(0)

test()

