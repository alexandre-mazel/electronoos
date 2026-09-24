import argparse
import cv2
import numpy as np
import random
import os
if os.name != "nt":
    from insightface.app import FaceAnalysis
    from insightface.model_zoo import get_model


"""
mkdir -p models && wget -O models/inswapper_128.onnx https://github.com/deepinsight/insightface/releases/download/model-zoo/inswapper_128.onnx

syntaxe:
python generate_faceswap.py painting.jpg visitor.jpg -n 1 -o result.jpg

scp a@192.168.0.45:/home/a/dev/git/electronoos/ego_musee/result.png \tmp

scp -P 45022 C:/Users/alexa/dev/git/electronoos/ego_musee/paintings/* a@engrenage.studio:/home/a/dev/git/electronoos/ego_musee/paintings/
scp -P 45022 a@engrenage.studio:/home/a/dev/git/electronoos/ego_musee/generated/* C:/Users/alexa/dev/git/electronoos/ego_musee/generated/

Ca rocks serieux, et on peut cascader en reutilisant la sortie comme ref d'entree

A faire avant: lancer le venv de ce dossier
"""


MODEL = "models/inswapper_128.onnx"

import cv2
import time

app = None
swapper = None

def create_generator():
    global app, swapper
    
    if app != None:
        return
    
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
    
    

def image_fullscreen_contain(image, screen_width, screen_height):
    """
    adapte l'image a la taille de l'ecran sans la deformer
    """
    image_height, image_width = image.shape[:2]

    scale = min(
        screen_width / image_width,
        screen_height / image_height
    )

    new_width = int(image_width * scale)
    new_height = int(image_height * scale)

    resized_image = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )

    fullscreen_image = np.zeros(
        (screen_height, screen_width, 3),
        dtype=np.uint8
    )

    x = (screen_width - new_width) // 2
    y = (screen_height - new_height) // 2

    fullscreen_image[
        y:y + new_height,
        x:x + new_width
    ] = resized_image

    return fullscreen_image

def get_painting_title(filename):
    #~ name = Path(filename).stem
    name = os.path.splitext( os.path.basename(filename) )[0]
    name = name.replace("_generated", "")
    name = name.replace("_-_", " - ")
    name = name.replace("_", " ")
    
    idx = name.find( " - Google" )
    if idx != -1:
        name = name[:idx]
    return name

def fade_images(image1_filename, image2_filename, duration=5.0):
    """
    Return False if user want to quit
    """
    
    img1 = cv2.imread(image1_filename)
    img2 = cv2.imread(image2_filename)

    if img1 is None:
        print( f"ERR: Cannot load image: {image1_filename}")
        return True
    if img2 is None:
        print( f"ERR: Cannot load image: {image2_filename}")
        return True

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
    
    sx,sy = 2736, 1824
    img1 = image_fullscreen_contain( img1, sx, sy )
    img2 = image_fullscreen_contain( img2, sx, sy )
    
    txt = get_painting_title( image1_filename )
    img1 = add_bottom_text( img1, txt )
    img2 = add_bottom_text( img2, txt )

    # Display first image
    cv2.imshow(window_name, img1)
    key = cv2.waitKey(5000) & 0xFF
    
    # ESC to interrupt
    if key == 27:
        return False
        
    # n to go to next image
    if key == ord("n"):
        return True

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
            
        # n to go to next image
        if key == ord("n"):
            return True

        if progress >= 1.0:
            break

    # Leave the second image displayed
    cv2.imshow(window_name, img2)
    cv2.waitKey(5000)

    #~ return window_name
    return True

def generate_swap( painting, person, output, num_face ):
    """
    num_face: 0..n-1
    """
    
    create_generator()

    print("Lecture des images...")

    scene = cv2.imread(painting)
    reference = cv2.imread(person)
    
    print( "size painting: %dx%d" % (scene.shape[1],scene.shape[0]) )
    print( "size person: %dx%d" % (reference.shape[1],reference.shape[0]) )
    
    if scene.shape[1] > 10000: # j'ai une image a 20k x 20k
        print( "ERR: sceen too big" )
        return

    if scene is None:
        raise RuntimeError(f"Impossible de lire {painting}")

    if reference is None:
        raise RuntimeError(f"Impossible de lire {person}")

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
            f"Visage {num_face} inexistant. "
            f"La scène contient {len(scene_faces)} visage(s)."
        )

    # On prend le premier visage de l'image de référence
    source_face = reference_faces[0]

    target_face = scene_faces[face_index]

    print(
        f"Remplacement du visage {num_face}..."
    )

    result = swapper.get(
        scene,
        target_face,
        source_face,
        paste_back=True
    )

    cv2.imwrite( output, result)

    print(f"Résultat enregistré : {output}")

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
    
    
    generate_swap( args.scene, args.face, args.output, args.face_number - 1 )
    
def add_postfix( filename, postfix ):
    base, extension = os.path.splitext(filename)
    new_filename = base + postfix + extension
    return new_filename
    
def add_bottom_text(image, text):
    height, width = image.shape[:2]

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness
    )

    text_width, text_height = text_size

    padding_top = 15
    padding_bottom = 15

    banner_height = (
        text_height +
        baseline +
        padding_top +
        padding_bottom
    )

    result = image.copy()

    # Bandeau noir en bas
    cv2.rectangle(
        result,
        (0, height - banner_height),
        (width, height),
        (0, 0, 0),
        -1
    )

    # Texte centré horizontalement
    text_x = (width - text_width) // 2
    text_y = (
        height -
        padding_bottom -
        baseline
    )

    cv2.putText(
        result,
        text,
        (text_x, text_y),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )

    return result
    
def render_pair_loop():
    srcpath = "paintings/"
    dstpath = "generated/"
    listfiles = os.listdir( srcpath )
    while 1:
        idx = random.randint(0,len(listfiles)-1)
        asrc = srcpath+listfiles[idx]
        postfix = "_generated"
        if random.random() > 0.5:
            postfix += "3"
            if random.random() > 0.3 and 0:
                postfix += "2"
        adst = dstpath+add_postfix( listfiles[idx], postfix )
        print("'%s' and '%s'" % (asrc,adst) )
        if os.path.isfile( asrc ) and os.path.isfile( adst ):
            print( "fading..." )
            if not fade_images( asrc, adst, 10 ):
                break

def generate_all():
    srcpath = "paintings/"
    dstpath = "generated/"
    listfiles = os.listdir( srcpath )
    for f in listfiles:
        asrc = srcpath + f
        adst = dstpath+add_postfix( f, "_generated3" )
        if os.path.isfile( asrc ) and not os.path.isfile( adst ):
            generate_swap( asrc, "visitor3.jpg", adst, 0 )
    

if __name__ == "__main__":
    # main()
    #~ generate_all()
    render_pair_loop()