---
title: TP1 - Données EXIF
description: Écriture d'un programme Python permettant d'extraire les données EXIF d'une image
---

# Données EXIF

## Introduction

**EXIF** *([:material-link: EXchangeable Image file Format](https://fr.wikipedia.org/wiki/Exchangeable_image_file_format))* est une spécification de **métadonnées** intégrées aux images au format JPEG ou TIFF produites par les appareils photographiques numériques.

L'objectif de ces travaux pratiques est de lire les données EXIF en provenance d'une image fournie au format JPEG.
Cela nécessitera l'utilisation des fonctions de parcours d'un dictionnaire.

## Préparation

### Espace de travail

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'application <i class="icon file-explorer"></i> **Explorateur de fichiers** 
           <span class="keys shortcut"><kbd>:fontawesome-brands-windows:</kbd><span>+</span><kbd>E</kbd></span>
        2. Dans le dossier `Document`, s'il n'y a pas de dossier nommé `NSI`, créez-le
        3. Dans le dossier `NSI`, créez le dossier `chapitre_11`
        4. Dans le dossier `chapitre_11` créez le dossier `tp1_exif`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier `NSI`, créez-le
        3. Dans le dossier `NSI`, créez le dossier `chapitre_11`
        4. Dans le dossier `chapitre_11` créez le dossier `tp1_exif`

### Téléchargement des fichiers

Pour réaliser ces travaux pratiques, il est nécessaire de disposer de certains fichiers.

!!! note "Récupération des fichiers"

    1. Téléchargez le fichier ZIP contenant les fichiers nécessaires : [:material-download: télécharger](assets/NSI1RE11_TP1.zip){:download="NSI1RE11_TP1.zip"}
    2. Ouvrez le fichier ZIP<br>*(si le navigateur ne l'ouvre automatiquement, cliquez sur le fichier téléchargé)*
    3. Sélectionnez tous les fichiers et dossiers  <span class="shortcut">++ctrl+a++</span>
    4. Copiez tous les fichiers et dossiers <span class="shortcut">++ctrl+c++</span>
    5. Collez les fichiers dans le dossier `NSI\chapitre_11\tp1_exif` <span class="shortcut">++ctrl+v++</span>

### Bibliothèque Pillow

Vous allez maintenant vérifier que la bibliothèque **Pillow** soit bien disponible dans votre environnement Python.

!!! note "Instructions - Vérification de la bibliothèque Pillow"

    1. Accédez à votre console Python
    2. Exécutez les instructions suivantes :
       ```python
       import PIL
       print('PIL', PIL.__version__)
       ```
    3. Si un message d'erreur s'affiche, installez la bibliothèque Pillow.

!!! warning "Attention - Vous rencontrez des problème avec l'installation de Pillow"

    Si vous n'arrivez pas à installer la bibliothèque Pillow, passez sous Basthon en suivant les instructions suivantes :

    1. Rendez-vous sur le site web [:material-link: basthon.fr](https://basthon.fr){:target="_blank"}
    2. Accédez à la console Python
    3. Chargez le fichier `exif.py` en tant que module 
    4. Chargez le fichier `photo.jpg`


## Mise en pratique

### Lecture des données EXIF

Pour commencer ces travaux pratiques, vous allez vous assurer du bon fonctionnement de l'accès aux données EXIF d'une image numérique.

Le fichier `exif.py` a été créé par votre enseignant afin de vous faciliter l'accès aux données EXIF d'une image numérique.
Le module `exif` ne comporte qu'une fonction dont il vous faut comprendre le fonctionnement.

!!! note "Instructions - Découverte du module `exif`"

    1. Ouvrez le fichier `exif.py`
    2. Lisez la *docstring* de la fonction `extraire_exif` afin de comprendre comment l'utiliser

!!! note "Instructions - Lecture des données EXIF"

    1. Ouvrez le fichier `main.py` *(vide)*
    2. Importez le module `exif`
    3. Ajoutez un appel à la fonction `extraire_exif` afin d'afficher la valeur retournée pour le fichier `photo.jpg`

!!! danger "Important"

    Tout le travail est à effectuer dans le fichier `main.py`. Le fichier `exif.py` **NE DOIT PAS** être modifié.

!!! question "Observations"

    - Confirmez-vous qu'un dictionnaire a été renvoyé par la fonction ?
    - Arrivez-vous à reconnaître certaines informations ? 
    - Quels sont les descripteurs de celles-ci ?


### Descripteurs EXIF

Les données EXIF telles qu'extraites du fichier `photo.jpg`, sont comparables à un *p*-uplet nommé que l'on représente en Python en utilisant un **dictionnaire**.

!!! info "Les dictionnaires"
    
    Un dictionnaire est un type contruit, c'est à dire qu'il est défini à partir d'un ou plusieurs autres types de données. 
    Il est consitué de clés auxquelles sont associé une valeur.
    La clé est toujours une chaîne de caractères.
    La valeur peut être de type quelconque.

    ```python
        { "clé 1": valeur, "clé 2": valeur, "clé 3": valeur, ..., "clé p": valeur }
    ```

Nous souhaitons disposer de la liste des descripteurs des données EXIF.

!!! note "Instructions - Liste des descripteurs"

    1. Ouvrez le fichier `main.py`
    2. Supprimez l'appel à la fonction `extraire_exif` du précédent exercice
    3. Implémentez la fonction `afficher_descripteurs_exif` ayant pour paramètre `nom_fichier` et qui affiche l'ensemble des clés du dictionnaire renvoyé par la fonction `extraire_exif`
    4. Testez la fonction dans la console Python en l'appelant sur le fichier `photo.jpg`

###  Informations sur l'appareil

Nous souhaitons connaître la marque (clé `Make`) et le modèle (clé `Model`) de l'appareil utilisé pour prendre la photo ainsi que son objectif (clé `LensModel`).

!!! example "Exemple d'affichage des informations de l'appareil"

    ```
    Marque   :  Apple
    Modèle   :  iPhone 8
    Objectif :  iPhone 8 back camera 3.99mm f/1.8
    ```

!!! note "Instructions - Affichage des informations sur l'appareil"

    1. Ouvrez le fichier `main.py`
    2. Écrivez la fonction `afficher_appareil` qui a pour paramètre `nom_fichier` et qui affiche ces trois informations
    3. Testez la fonction dans la console Python en l'appelant sur le fichier `photo.jpg`

### Intégralité des informations
Nous souhaitons disposer de toutes les informations EXIF sous la forme suivante :

!!! example "Exemple d'affichage des données EXIF"

    ```
    ExifImageWidth : 4032
    FocalLengthIn35mmFilm : 28
    SceneCaptureType : 0
    SubsecTimeOriginal : 255
    ...
    ```

!!! note "Instructions - Affichage des informations sur l'appareil"

    1. Ouvrez le fichier `main.py`
    2. Écrivez la fonction `afficher_exif` qui a pour paramètre `nom_fichier` et qui affiche l'ensemble des informations EXIF
    3. Testez la fonction dans la console Python en l'appelant sur le fichier `photo.jpg`

!!! success "Observations"

    Votre fonction `afficher_exif` fonctionne-t-elle ? Si oui, testez-la sur une autre photo de votre choix, provenant de votre téléphone ou trouvée sur le Web.