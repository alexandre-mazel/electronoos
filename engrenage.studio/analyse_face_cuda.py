import cv2
import numpy as np
import insightface

_face_app = None


def compare_faces(image1_path, image2_path):
    global _face_app

    if _face_app is None:
        _face_app = insightface.app.FaceAnalysis(
            name = "buffalo_l",
            providers = [
                "CUDAExecutionProvider",
                "CPUExecutionProvider"
            ]
        )
        _face_app.prepare(
            ctx_id = 0,
            det_size = (640, 640)
        )

    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    if image1 is None:
        raise ValueError("Unable to read image 1")

    if image2 is None:
        raise ValueError("Unable to read image 2")

    faces1 = _face_app.get(image1)
    faces2 = _face_app.get(image2)

    if len(faces1) == 0:
        raise ValueError("No face detected in image 1")

    if len(faces2) == 0:
        raise ValueError("No face detected in image 2")

    embedding1 = faces1[0].normed_embedding
    embedding2 = faces2[0].normed_embedding

    similarity = float(np.dot(embedding1, embedding2))

    return similarity