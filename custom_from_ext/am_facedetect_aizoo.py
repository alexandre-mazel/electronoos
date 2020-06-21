# -*- coding:utf-8 -*-
import cv2
import time
import argparse

import numpy as np
from PIL import Image
#from keras.models import model_from_json

import sys
import os
sys.path.append( os.path.expanduser("~/dev/FaceMaskDetection/") )
from utils.anchor_generator import generate_anchors
from utils.anchor_decode import decode_bbox
from utils.nms import single_class_non_max_suppression
from load_model.tensorflow_loader import load_tf_model, tf_inference

class MaskDetector:
    
    def __init__( self ):
        pass
        
    def loadModels( self, strMaskClassificationModel = 'models/face_mask_detection.pb' ):
        print("INF: MaskDetector.loadModels: loading models..." )
        
        try:
            self.sess, self.graph = load_tf_model( strMaskClassificationModel )
        except:
            self.sess, self.graph = load_tf_model( os.path.expanduser("~/dev/FaceMaskDetection/") + strMaskClassificationModel )
        # anchor configuration
        feature_map_sizes = [[33, 33], [17, 17], [9, 9], [5, 5], [3, 3]]
        anchor_sizes = [[0.04, 0.056], [0.08, 0.11], [0.16, 0.22], [0.32, 0.45], [0.64, 0.72]]
        anchor_ratios = [[1, 0.62, 0.42]] * 5

        # generate anchors
        anchors = generate_anchors(feature_map_sizes, anchor_sizes, anchor_ratios)

        # for inference , the batch size is 1, the model output shape is [1, N, 4],
        # so we expand dim for anchors to [1, anchor_num, 4]
        self.anchors_exp = np.expand_dims(anchors, axis=0)

        self.id2class = {0: 'Mask', 1: 'NoMask'}
        
        # preload everything
        self.detectFromImage(np.zeros((128,128,3), np.uint8), bShowResults = False )
        
        print("INF: MaskDetector.loadModels: end..." )
        
    def classToStr(self, nNumClass):
        return self.id2class[nNumClass]

    def detectFromImageFile( self, strFilename, bShowResults = True ):
        im = cv2.imread( strFilename )
        return self.detectFromImage( im, bShowResults=bShowResults )
        
    def detectFromImage( self, img, bShowResults = True ):
        img = cv2.cvtColor( img, cv2.COLOR_BGR2RGB )
        detectedFaces = self._inference(img, show_result=bShowResults, target_shape=(260, 260))
        retVal = []
        rConfidenceItsAFace = 0.8 # we don't have this info currently
        properties = ["mask", 0, 0.]
        for detected in detectedFaces:
            if detected[0] == 0:
                properties[1] = 1
            else:
                properties[1] = 0
            properties[2] = detected[1]
            data = [detected[2:], rConfidenceItsAFace, properties]
            retVal.append(data)
        return retVal

    def _inference(self, image,
                  conf_thresh=0.5,
                  iou_thresh=0.4,
                  target_shape=(160, 160),
                  draw_result=True,
                  show_result=True
                  ):
        '''
        Main function of detection inference
        :param image: 3D numpy array of image
        :param conf_thresh: the min threshold of classification probabity.
        :param iou_thresh: the IOU threshold of NMS
        :param target_shape: the model input size.
        :param draw_result: whether to daw bounding box to the image.
        :param show_result: whether to display the image.
        :return:
            [class_id, conf, xmin, ymin, xmax, ymax]
        '''
        # image = np.copy(image)
        output_info = []
        height, width, _ = image.shape
        image_resized = cv2.resize(image, target_shape)
        image_np = image_resized / 255.0  # 归一化到0~1
        image_exp = np.expand_dims(image_np, axis=0)
        y_bboxes_output, y_cls_output = tf_inference(self.sess, self.graph, image_exp)

        # remove the batch dimension, for batch is always 1 for inference.
        y_bboxes = decode_bbox(self.anchors_exp, y_bboxes_output)[0]
        y_cls = y_cls_output[0]
        # To speed up, do single class NMS, not multiple classes NMS.
        bbox_max_scores = np.max(y_cls, axis=1)
        bbox_max_score_classes = np.argmax(y_cls, axis=1)

        # keep_idx is the alive bounding box after nms.
        keep_idxs = single_class_non_max_suppression(y_bboxes,
                                                     bbox_max_scores,
                                                     conf_thresh=conf_thresh,
                                                     iou_thresh=iou_thresh,
                                                     )

        if not show_result: draw_result  = False
        for idx in keep_idxs:
            conf = float(bbox_max_scores[idx])
            class_id = bbox_max_score_classes[idx]
            bbox = y_bboxes[idx]
            # clip the coordinate, avoid the value exceed the image boundary.
            xmin = max(0, int(bbox[0] * width))
            ymin = max(0, int(bbox[1] * height))
            xmax = min(int(bbox[2] * width), width)
            ymax = min(int(bbox[3] * height), height)

            if draw_result:
                if class_id == 0:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
                cv2.putText(image, "%s: %.2f" % (self.id2class[class_id], conf), (xmin + 2, ymin - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
            output_info.append([class_id, conf, xmin, ymin, xmax, ymax])

        if show_result:
            Image.fromarray(image).show()
        return output_info

# class MaskDetector - end

def run_on_video(video_path, output_video_name, conf_thresh):
    cap = cv2.VideoCapture(video_path)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # writer = cv2.VideoWriter(output_video_name, fourcc, int(fps), (int(width), int(height)))
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if not cap.isOpened():
        raise ValueError("Video open failed.")
        return
    status = True
    idx = 0
    while status:
        start_stamp = time.time()
        status, img_raw = cap.read()
        img_raw = cv2.cvtColor(img_raw, cv2.COLOR_BGR2RGB)
        read_frame_stamp = time.time()
        if (status):
            inference(img_raw,
                      conf_thresh,
                      iou_thresh=0.5,
                      target_shape=(260, 260),
                      draw_result=True,
                      show_result=False)
            cv2.imshow('image', img_raw[:, :, ::-1])
            cv2.waitKey(1)
            inference_stamp = time.time()
            # writer.write(img_raw)
            write_frame_stamp = time.time()
            idx += 1
            print("%d of %d" % (idx, total_frames))
            print("read_frame:%f, infer time:%f, write time:%f" % (read_frame_stamp - start_stamp,
                                                                   inference_stamp - read_frame_stamp,
                                                                   write_frame_stamp - inference_stamp))
    # writer.release()

if __name__ == "__main__":
    totalScriptTimeBegin = time.time()
    parser = argparse.ArgumentParser(description="Face Mask Detection")
    parser.add_argument('--img-mode', type=int, default=1, help='set 1 to run on image, 0 to run on video.')
    parser.add_argument('--img-path', type=str, help='path to your image.')
    parser.add_argument('--video-path', type=str, default='0', help='path to your video, `0` means to use camera.')
    parser.add_argument('--show', type=bool, default = False, help ='show results' )
    # parser.add_argument('--hdf5', type=str, help='keras hdf5 file')
    args = parser.parse_args()
    
    md = MaskDetector()
    md.loadModels( 'models/face_mask_detection.pb' )
    
    if args.img_mode:
        imgPath = args.img_path
        md.detectFromImageFile(imgPath, bShowResults=args.img_path)
        print( "INF: measuring time..." )
        timeBegin = time.time()
        md.detectFromImageFile(imgPath, bShowResults=False)
        print("INF: measured time: %5.3fs" % (time.time()-timeBegin) )
    else:
        video_path = args.video_path
        if args.video_path == '0':
            video_path = 0
        run_on_video(video_path, '', conf_thresh=0.5)

    print("INF: total script time: %5.2fs" % (time.time()-totalScriptTimeBegin) )