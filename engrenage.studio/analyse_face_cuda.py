import cv2
import numpy as np
import insightface # pip install insightface # will download https://github.com/deepinsight/insightface/releases/download/model-zoo/buffalo_l.zip
import time

"""
Attention des fois le modele ne se desarchive pas comme il faut:
     return get_embed_faces( im )
  File "C:/Users/alexa/dev/git/electronoos/engrenage.studio/analyse_face_cuda.py", line 498, in get_embed_faces
    _face_app = insightface.app.FaceAnalysis(
  File "C:/Python39/lib/site-packages/insightface/app/face_analysis.py", line 61, in __init__
    assert 'detection' in self.models
AssertionError
=> deplacer HOME/.insightface/models/antelopev2/antelopev2 dans le ..


Pour utiliser le gpu sur ubuntu:
J'ai du deinstaller pip install onnxruntime et mettre pip install onnxruntime-gpu
pip uninstall onnxruntime
pip install onnxruntime-gpu
#mais en fait:
pip uninstall -y onnxruntime-gpu
pip install "onnxruntime-gpu==1.26.0"

pour voir la sortie: lancer vcxsrv au lieu de xming
et lancer sur le remote: xfwm4 --compositor=off &
afin de pouvoir redimensionner la fenetre scite plus tranquillement
"""

_face_app = None
def getInsightApp():
    global _face_app
    
    strModel = "buffalo_l"
    strModel = "antelopev2" # vaguement meilleur (cf bench_faces_2026 dans le git face_tools) 
    """
    et plus tard:
    git clone https://github.com/yakhyo/adaface-onnx.git
    cd adaface-onnx
    pip install -r requirements.txt
    bash download.sh
    # Le projet fournit directement les poids ONNX AdaFace et un exemple d'utilisation.
    """

    if _face_app is None:
        _face_app = insightface.app.FaceAnalysis(
            name = strModel,  
            providers = [
                #~ "TensorrtExecutionProvider", # ne fonctionne pas
                "CUDAExecutionProvider",
                "CPUExecutionProvider"
            ]
        )
        _face_app.prepare(
            ctx_id = 0,
            det_size = (640, 640)
        )
        
    return _face_app
    

def find_most_centered_and_big_face(faces, image_width, image_height,verbose=0):
    """
    return the index of the most centered faces (and also big enough)
    """
    
    if not faces:
        return -1
    

    image_cx = image_width / 2.0
    image_cy = image_height / 2.0
    
    if verbose: print( "DBG: find_most_centered_and_big_face: centrx: %d, centry: %d" % (image_cx,image_cy) )

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

        distance = ( (cx - image_cx) ** 2 + (cy - image_cy) ** 2 ) ** 0.5

        # 0 = centre, 1 = bord extreme
        normalized_distance = distance / max_distance

        # 1 au centre, 0.5 a une distance normalisee de 1
        centering_factor = 1.0 / (1.0 + normalized_distance)

        score = area * centering_factor ** 4 # add an importance to the centering
        
        if verbose: print( "index: %d, lefttop: %d,%d, rightbottom: %d,%d centering_factor: %.2f, area: %.1f, score: %.1f" % (i,x1,y1,x2,y2,centering_factor,area,score) )

        if score > best_score:
            best_score = score
            best_index = i

    return best_index

import cv2


def draw_faces_rect(image1, faces1, selected_idx, result = None ):
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

        label = f"{i}: {gender}, {age}"
        
        if i == selected_idx and result != None:
            label += " => %s" % result

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

    return image
    
import numpy as np
from sklearn.cluster import KMeans


def select_cluster_representatives( embeddings, n_clusters=5, random_state=42, normalize=True ):
    """
    Regroupe des embeddings supposés appartenir à une même personne
    en n_clusters groupes, puis retourne pour chaque cluster
    l'embedding RÉEL de la liste qui est le plus proche du centre
    du cluster.

    Parameters
    ----------
    embeddings : array-like, shape (N, D)
        Liste des embeddings.

    n_clusters : int
        Nombre de clusters / représentants souhaités.

    random_state : int
        Seed pour rendre KMeans reproductible.

    normalize : bool
        Si True, normalise les embeddings avant clustering.
        Recommandé pour AdaFace.

    Returns
    -------
    representatives : np.ndarray, shape (n_clusters, D)
        Les embeddings originaux sélectionnés comme représentants.

    cluster_indices : np.ndarray, shape (n_clusters,)
        Indices dans la liste originale correspondant aux représentants.

    labels : np.ndarray, shape (N,)
        Cluster auquel appartient chaque embedding.

    """

    X = np.asarray(embeddings, dtype=np.float32)

    if X.ndim != 2:
        raise ValueError(
            f"embeddings doit être de forme (N, D), reçu {X.shape}"
        )

    N, D = X.shape

    if N < n_clusters:
        raise ValueError(
            f"Impossible de créer {n_clusters} clusters avec seulement {N} embeddings."
        )

    # Normalisation des embeddings
    if normalize:
        norms = np.linalg.norm(X, axis=1, keepdims=True)

        if np.any(norms == 0):
            raise ValueError("Un embedding possède une norme nulle.")

        X = X / norms

    # K-Means
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10,
    )

    labels = kmeans.fit_predict(X)

    representatives = []
    representative_indices = []

    # Pour chaque cluster
    for cluster_id in range(n_clusters):

        indices = np.where(labels == cluster_id)[0]
        cluster = X[indices]

        # Centroïde du cluster
        centroid = cluster.mean(axis=0)

        # Pour des embeddings normalisés, on renormalise
        # le centroïde avant de calculer la similarité cosinus.
        centroid_norm = np.linalg.norm(centroid)

        if centroid_norm > 0:
            centroid = centroid / centroid_norm

        # Similarité cosinus avec le centroïde
        similarities = cluster @ centroid

        # Embedding réel le plus proche du centroïde
        local_idx = np.argmax(similarities)

        original_idx = indices[local_idx]

        representatives.append(X[original_idx])
        representative_indices.append(original_idx)

    representatives = np.stack(representatives)
    representative_indices = np.asarray(representative_indices)

    return representatives, representative_indices, labels
    
import numpy as np


def cluster_metrics(embeddings, representatives, labels):
    """
    Calcule des métriques de compacité pour les clusters.

    Parameters
    ----------
    embeddings : array-like, shape (N, D)
        Tous les embeddings originaux.

    representatives : array-like, shape (K, D)
        Embeddings représentants retournés par
        select_cluster_representatives().

    labels : array-like, shape (N,)
        Labels retournés par select_cluster_representatives().

    Returns
    -------
    metrics : list[dict]
        Une entrée par cluster.
    """

    X = np.asarray(embeddings, dtype=np.float32)
    representatives = np.asarray(representatives, dtype=np.float32)
    labels = np.asarray(labels)

    # Normalisation
    X = X / np.linalg.norm(X, axis=1, keepdims=True)
    representatives = (
        representatives /
        np.linalg.norm(representatives, axis=1, keepdims=True)
    )

    n_clusters = len(representatives)

    metrics = []

    for cluster_id in range(n_clusters):

        mask = labels == cluster_id
        cluster = X[mask]

        n = len(cluster)

        if n == 0:
            continue

        # Centroïde du cluster
        centroid = cluster.mean(axis=0)
        centroid /= np.linalg.norm(centroid)

        # Similarité cosinus de chaque embedding au centroïde
        similarities = cluster @ centroid

        # Similarité du représentant sélectionné
        representative = representatives[cluster_id]
        representative_similarity = representative @ centroid

        # Conversion en distance angulaire
        angles = np.arccos(
            np.clip(similarities, -1.0, 1.0)
        )

        angles_deg = np.degrees(angles)

        metrics.append({
            "cluster": cluster_id,

            # Nombre d'images
            "n": n,

            # Représentativité de l'embedding choisi
            "representative_similarity": float(
                representative_similarity
            ),

            # Similarité moyenne au centre
            "mean_similarity": float(
                similarities.mean()
            ),

            # Dispersion des similarités
            "std_similarity": float(
                similarities.std()
            ),

            # Distance angulaire moyenne
            "mean_angle_deg": float(
                angles_deg.mean()
            ),

            # Rayon contenant environ 95% des images
            "radius_95_deg": float(
                np.percentile(angles_deg, 95)
            ),

            # Image la plus éloignée
            "max_angle_deg": float(
                angles_deg.max()
            ),
        })

    return metrics
    
    TODO: clustering
    
"""

Utilisation

Avec ta fonction précédente :

representatives, indices, labels = select_cluster_representatives(
    embeddings,
    n_clusters=5
)

metrics = cluster_metrics(
    embeddings,
    representatives,
    labels
)

for m in metrics:
    print(m)


Tu pourrais obtenir quelque chose comme :

Cluster 0
    n = 42
    representative_similarity = 0.981
    mean_similarity          = 0.973
    std_similarity           = 0.011
    mean_angle_deg           = 12.1°
    radius_95_deg            = 18.4°
    max_angle_deg            = 27.2°

Cluster 1
    n = 31
    representative_similarity = 0.992
    mean_similarity          = 0.987
    std_similarity           = 0.006
    mean_angle_deg           = 9.1°
    radius_95_deg            = 13.7°
    max_angle_deg            = 19.2°

Celle que je regarderais en priorité

Pour mesurer la largeur du cluster, utilise :

radius_95_deg


Par exemple :

12
"""

def order_faces( faces ):
    """
    Order faces from left to right, then from top to bottom.

    For example, in a group photo, the top-left face is assigned
    index 0, the face immediately to its right gets index 1, and so on.
    Once the first row is completed, the faces on the next row are
    ordered from left to right, continuing the numbering.
    return the ordored structure
    """
    if not faces:
        return []

    heights = [
        face.bbox[3] - face.bbox[1]
        for face in faces
    ]

    row_tolerance = np.median( heights ) * 0.5

    sorted_faces = sorted(
        faces,
        key = lambda face: ( face.bbox[1] + face.bbox[3] ) / 2
    )

    rows = []

    for face in sorted_faces:
        center_y = ( face.bbox[1] + face.bbox[3] ) / 2

        matching_row = None
        smallest_distance = float( "inf" )

        for row in rows:
            distance = abs( center_y - row["center_y"] )

            if distance <= row_tolerance and distance < smallest_distance:
                matching_row = row
                smallest_distance = distance

        if matching_row is None:
            rows.append(
                {
                    "center_y": center_y,
                    "faces": [ face ],
                }
            )
        else:
            matching_row["faces"].append( face )
            matching_row["center_y"] = sum(
                ( item.bbox[1] + item.bbox[3] ) / 2
                for item in matching_row["faces"]
            ) / len( matching_row["faces"] )

    rows.sort( key = lambda row: row["center_y"] )

    ordered_faces = []

    for row in rows:
        row["faces"].sort(
            key = lambda face: ( face.bbox[0] + face.bbox[2] ) / 2
        )
        ordered_faces.extend( row["faces"] )

    return list( enumerate( ordered_faces ) )


def get_embed_faces( im, bOnlyMostCentered = False ):
    fap = getInsightApp()
        
    faces = fap.get(im)
    
    #~ print( "DBG: get_embed_faces: faces before: " + str(faces) )
    
    if bOnlyMostCentered:
        idx = find_most_centered_and_big_face( faces, im.shape[1], im.shape[0] )
        faces = [faces[idx]]
    else:
        faces = order_faces( faces )
        
    #~ print( "DBG: get_embed_faces: faces after: " + str(faces) )
        
    return faces
    
def  get_embed_faces_from_filename( filename, bOnlyMostCentered = False ):

    im = cv2.imread(filename)

    if im is None:
        print( "ERR: get_embed_faces_from_filename: can't read image '%s'" % filename )
        return []
    return get_embed_faces( im, bOnlyMostCentered=bOnlyMostCentered )
    
    
def compare_faces(image1_path, image2_path, verbose = 0 ):
    
    fap = getInsightApp()

    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    if image1 is None:
        raise ValueError("Unable to read image 1")

    if image2 is None:
        raise ValueError("Unable to read image 2")

    faces1 = fap.get(image1)
    faces2 = fap.get(image2)

    if len(faces1) == 0:
        raise ValueError("No face detected in image 1")

    if len(faces2) == 0:
        raise ValueError("No face detected in image 2")
        
    idx1 = find_most_centered_and_big_face( faces1, image1.shape[1], image1.shape[0],verbose=verbose )
    idx2 = find_most_centered_and_big_face( faces2, image2.shape[1], image2.shape[0],verbose=verbose )
    
    print("faces1: taking idx: %s" % str( idx1 ) )
    print("faces2: taking idx: %s" % str( idx2 ) )
    
    embedding1 = faces1[idx1].normed_embedding
    embedding2 = faces2[idx2].normed_embedding

    similarity = float(np.dot(embedding1, embedding2))
    
    
    if verbose: 
        imdebug1 = draw_faces_rect( image1, faces1, idx1 )
        imdebug2 = draw_faces_rect( image2, faces2, idx2, similarity )
        
        
        cv2.namedWindow("im1", cv2.WINDOW_NORMAL)
        cv2.namedWindow("im2", cv2.WINDOW_NORMAL)
        xr = 1200
        yr = 1000
        cv2.resizeWindow("im1", xr, yr)
        cv2.resizeWindow("im2", xr, yr)
        cv2.moveWindow( "im1", 0, 0 )
        cv2.moveWindow( "im2", xr+20, 0 )

        cv2.imshow( "im1", imdebug1 )
        cv2.imshow( "im2", imdebug2 )
        cv2.waitKey(0)

    return similarity
    
    
def test_quick_compare():
    verbose = 1
    verbose = 0
    
    imgs = ["20240102_105013_small","20240109_161443_small","20240223_094710_small","20260906_210413_small"]
    path_template = "../test/%s.jpg"
    
    time_begin = time.time()
    compare_faces( path_template % imgs[0], path_template % imgs[1],verbose=0 )
    
    time_no_load = time.time()
    
    nbr_embed = 0
    for i1 in range(len(imgs)-1):
        for i2 in range(i1+1,len(imgs)):
            pi1 = path_template % imgs[i1]
            pi2 = path_template % imgs[i2]
            simi = compare_faces( pi1, pi2,verbose=verbose )
            print( "%s & %s => %.3f" % ( imgs[i1], imgs[i2], simi ) )
            nbr_embed += 2
        print("")
        
    duration = time.time() - time_begin
    duration_just_detect = time.time() - time_no_load
    print( "duration total: %.1fs" % duration )
    print( "duration just detect: %.2fs (%.3fs per embed)" % (duration_just_detect,duration_just_detect/nbr_embed ) )
    """
    
    antelopev2
    
                                        Total           just detect             per embed
    mstab7                          33/40         26/30                   2.21/3.75
    champion1 cpu               13.2            10.1                    0.844
    champion1 RTX3080       2.9             0.31                    0.026
    
    buffalo_l
    champion1 RTX3080       2.7             0.27                    0.022
    
    """
    
def test_face_ordering():
    faces = get_embed_faces_from_filename( "../test/20240109_161443_small.jpg" )

    
def autotest():
    test_quick_compare()
    test_face_ordering()

    
    
if __name__ == "__main__":
    autotest()