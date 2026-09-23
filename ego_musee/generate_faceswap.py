import argparse
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model

"""
mkdir -p models && wget -O models/inswapper_128.onnx https://github.com/deepinsight/insightface/releases/download/model-zoo/inswapper_128.onnx

syntaxe:
python generate_faceswap.py painting.jpg visitor.jpg -n 1 -o result.jpg

scp a@192.168.0.45:/home/a/dev/git/electronoos/ego_musee/result.png \tmp

Ca rocks serieux, et on peut cascader en reutilisant la sortie comme ref d'entree
"""


MODEL = "models/inswapper_128.onnx"


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

    scene = cv2.imread(args.scene)
    reference = cv2.imread(args.face)

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

    face_index = args.face_number - 1

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

    cv2.imwrite(args.output, result)

    print(f"Résultat enregistré : {args.output}")


if __name__ == "__main__":
    main()