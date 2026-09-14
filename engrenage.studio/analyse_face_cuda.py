import cv2
import numpy as np
import insightface # pip install insightface # will download https://github.com/deepinsight/insightface/releases/download/model-zoo/buffalo_l.zip

_face_app = None

def find_most_centered_and_big_face(faces, image_width, image_height):
    """
    return the index of the most centered faces (and also big enough)
    """
    
    if not faces:
        return -1

    image_cx = image_width / 2.0
    image_cy = image_height / 2.0

    # Distance maximale possible au centre
    max_distance = (
        (image_cx ** 2) +
        (image_cy ** 2)
    ) ** 0.5

    best_index = None
    best_score = -float("inf")

    for i, face in enumerate(faces):

        x1, y1, x2, y2 = face.bbox

        width = x2 - x1
        height = y2 - y1

        area = width * height

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        distance = (
            (cx - image_cx) ** 2 +
            (cy - image_cy) ** 2
        ) ** 0.5

        # 0 = centre, 1 = bord extreme
        normalized_distance = distance / max_distance

        # 1 au centre, 0.5 a une distance normalisee de 1
        centering_factor = 1.0 / (1.0 + normalized_distance)

        score = area * centering_factor

        if score > best_score:
            best_score = score
            best_index = i

    return best_index

import cv2


def draw_faces_rect(image1, faces1, selected_idx):
    """
    Draw all detected faces on image1.

    - Blue rectangle around non-selected faces
    - Green rectangle around selected face
    - Gender and age displayed beside each face

    Returns the annotated image.
    """

    image = image1.copy()

    for i, face in enumerate(faces1):

        x1, y1, x2, y2 = map(int, face.bbox)

        # Selected face = green, others = blue
        color = (0, 255, 0) if i == selected_idx else (255, 0, 0)

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        # InsightFace:
        # face.gender : 0 = female, 1 = male
        # face.age    : estimated age
        gender = "Male" if face.gender == 1 else "Female"
        age = int(round(face.age))

        label = f"{gender}, {age}"

        # Put label just above the bounding box
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        (text_width, text_height), baseline = cv2.getTextSize(
            label,
            font,
            font_scale,
            thickness
        )

        # Prefer above the bbox, otherwise put it below
        label_y = y1 - 8

        if label_y - text_height < 0:
            label_y = y2 + text_height + 8

        cv2.putText(
            image,
            label,
            (x1, label_y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )

    cv2.imshow("Faces", image)
    cv2.waitKey(0)

    return image
    
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
        
    idx1 = find_most_centered_and_big_face( faces1, image1.shape[1], image1.shape[0] )
    idx2 = find_most_centered_and_big_face( faces2, image2.shape[1], image2.shape[0] )
    
    draw_faces_rect( image1, faces1, idx1 )
    
    print("faces1: taking idx: %s" % str( idx1 ) )
    print("faces2: taking idx: %s" % str( idx2 ) )
    
    embedding1 = faces1[idx1].normed_embedding
    embedding2 = faces2[idx2].normed_embedding

    similarity = float(np.dot(embedding1, embedding2))

    return similarity
    
def autotest():
    imgs = ["20240102_105013_small","20240109_161443_small","20240223_094710_small","20260906_210413_small"]
    
    for img1 in imgs:
        for img2 in imgs:
            if img1 == img2:
                continue
            pi1 = "../test/%s.jpg" % img1
            pi2 = "../test/%s.jpg" % img2
            simi = compare_faces( pi1, pi2 )
            print( "%s & %s => %.3f" % ( img1, img2, simi ) )
        print("")
    
    
if __name__ == "__main__":
    autotest()