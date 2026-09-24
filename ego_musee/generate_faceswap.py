import argparse
import cv2
import numpy as np
import random
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model


"""
mkdir -p models && wget -O models/inswapper_128.onnx https://github.com/deepinsight/insightface/releases/download/model-zoo/inswapper_128.onnx

syntaxe:
python generate_faceswap.py painting.jpg visitor.jpg -n 1 -o result.jpg

scp a@192.168.0.45:/home/a/dev/git/electronoos/ego_musee/result.png \tmp

scp -P 45022 C:/Users/alexa/dev/git/electronoos/ego_musee/paintings/* a@engrenage.studio:/home/a/dev/git/electronoos/ego_musee/paintings/

Ca rocks serieux, et on peut cascader en reutilisant la sortie comme ref d'entree

A faire avant: lancer le venv de ce dossier
"""


MODEL = "models/inswapper_128.onnx"

import cv2
import time


def fade_images(image1_filename, image2_filename, duration=5.0):
    img1 = cv2.imread(image1_filename)
    img2 = cv2.imread(image2_filename)

    if img1 is None:
        raise ValueError(f"Cannot load image: {image1_filename}")
    if img2 is None:
        raise ValueError(f"Cannot load image: {image2_filename}")

    if img1.shape != img2.shape:
        raise ValueError("The two images must have exactly the same format/size.")

    window_name = "Paintings"

    # Create a borderless fullscreen window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        window_name,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    # Display first image
    cv2.imshow(window_name, img1)
    cv2.waitKey(5000)

    # Smooth fade
    start = time.perf_counter()

    while True:
        elapsed = time.perf_counter() - start
        progress = min(elapsed / duration, 1.0)

        # Linear interpolation between the two images
        blended = cv2.addWeighted(
            img1, 1.0 - progress,
            img2, progress,
            0
        )

        cv2.imshow(window_name, blended)

        # Keep the window responsive
        key = cv2.waitKey(16) & 0xFF

        # ESC to interrupt
        if key == 27:
            return False

        if progress >= 1.0:
            break

    # Leave the second image displayed
    cv2.imshow(window_name, img2)
    cv2.waitKey(1)

    return window_name
    return True

def generate_swap( painting, person, output, num_face ):
    """
    num_face: 0..n-1
    """

    scene = cv2.imread(painting)
    reference = cv2.imread(person)

    if scene is None:
        raise RuntimeError(f"Impossible de lire {args.scene}")

    if reference is None:
        raise RuntimeError(f"Impossible de lire {args.face}")

    print("Détection des visages...")

    scene_faces = app.get(scene)
    reference_faces = app.get(reference)

    print(f"Visages dans la scène     : {len(scene_faces)}")
    print(f"Visages dans la référence : {len(reference_faces)}")

    if len(scene_faces) == 0:
        raise RuntimeError("Aucun visage trouvé dans la scène.")

    if len(reference_faces) == 0:
        raise RuntimeError("Aucun visage trouvé dans l'image de référence.")

    face_index = num_face

    if face_index < 0 or face_index >= len(scene_faces):
        raise RuntimeError(
            f"Visage {args.face_number} inexistant. "
            f"La scène contient {len(scene_faces)} visage(s)."
        )

    # On prend le premier visage de l'image de référence
    source_face = reference_faces[0]

    target_face = scene_faces[face_index]

    print(
        f"Remplacement du visage {args.face_number}..."
    )

    result = swapper.get(
        scene,
        target_face,
        source_face,
        paste_back=True
    )

    cv2.imwrite( output, result)

    print(f"Résultat enregistré : {args.output}")

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "scene",
        nargs="?",
        default="painting.jpg",
        help="Image principale"
    )

    parser.add_argument(
        "face",
        nargs="?",
        default="visitor.jpg",
        help="Image contenant le visage de référence"
    )

    parser.add_argument(
        "-n",
        "--face-number",
        type=int,
        default=3,
        help="Numéro du visage à remplacer (1 = premier visage)"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="result.png"
    )

    args = parser.parse_args()

    print("Chargement du détecteur...")

    app = FaceAnalysis(
        name="buffalo_l",
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )

    app.prepare(
        ctx_id=0,
        det_size=(640, 640)
    )

    print("Chargement du modèle face swap...")

    swapper = get_model(
        MODEL,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )

    print("Lecture des images...")
    
    generate_swap( args.scene, args.face, args.output, args.face_number - 1 )
    
def render_pair_loop():
    srcpath = "paintings/"
    dstpath = "generated/"
    listfiles = os.listdir( srcpath )
    while 1:
        idx = random.randint(0,len(listfiles)-1)
        asrc = srcpath+listfiles[idx]
        adst = dstpath+listfiles[idx]
        adst = adst.replace( ".jpg", "_generated.jpg" )
        adst = adst.replace( ".png", "_generated.png" )
        print("'%s' and '%s'" % (asrc,adst) )
        if os.path.isfile( asrc ) and os.path.isfile( adst ):
            print( "fading..." )
            if not fade_images( asrc, adst ):
                break

def generate_all():
    srcpath = "paintings/"
    dstpath = "generated/"
    listfiles = os.listdir( srcpath )
    for f in listfiles:
        asrc = srcpath + f
        adst = dstpath + f.replace(".jpg","_generated.jpg").replace(".png","_generated.png" )
        if os.path.isfile( asrc ):
            generate_swap( asrc, "visitor.jpg", adst, 0 )
    

if __name__ == "__main__":
    # main()
    
    render_pair_loop()