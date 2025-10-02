---
title: TP2 - Compteur de mots
description: Écriture d'un programme Python permettant de compter les mots d'un document texte
---

# Compteur de mots

## Introduction

L'objectif de ces travaux pratiques est d'écrire un programme permettant de compter les mots d'un document texte.

## Préparation

### Espace de travail

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'application <i class="icon file-explorer"></i> **Explorateur de fichiers** 
           <span class="keys shortcut"><kbd>:fontawesome-brands-windows:</kbd><span>+</span><kbd>E</kbd></span>
        2. Dans le dossier `Document`, s'il n'y a pas de dossier nommé `NSI`, créez-le
        3. Dans le dossier `NSI`, s'il n'y a pas de dossier nommé `chapitre_11`, créez-le
        4. Dans le dossier `chapitre_11` créez le dossier `tp2_compteur_mots`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier `NSI`, créez-le
        3. Dans le dossier `NSI`, s'il n'y a pas de dossier nommé `chapitre_11`, créez-le
        4. Dans le dossier `chapitre_11` créez le dossier `tp2_compteur_mots`

### Téléchargement des fichiers

Pour réaliser ces travaux pratiques, il est nécessaire de disposer de certains fichiers.

!!! note "Récupération des fichiers"

    1. Téléchargez le fichier ZIP contenant les fichiers nécessaires : [:material-download: télécharger](assets/NSI1RE11_TP2.zip){:download="NSI1RE11_TP2.zip"}
    2. Ouvrez le fichier ZIP<br>*(si le navigateur ne l'ouvre automatiquement, cliquez sur le fichier téléchargé)*
    3. Sélectionnez tous les fichiers et dossiers  <span class="shortcut">++ctrl+a++</span>
    4. Copiez tous les fichiers et dossiers <span class="shortcut">++ctrl+c++</span>
    5. Collez les fichiers dans le dossier `NSI\chapitre_11\tp2_compteur_mots` <span class="shortcut">++ctrl+v++</span>


## Mise en pratique

### Fusion de dictionnaires

Le module `chaines` dispose d'une fonction `compter_mots` permettant de compter les mots d'une chaîne de caractères.
Celle-ci renvoie un dictionnaire contenant le nombre d'occurrences de chaque mot de cette chaîne.

!!! example "Exemple - Appel à la fonction `compter_mots`"

    ```
    >>> compter_mots('hello, world')
    {'hello': 1, 'world': 1}
    ```

Le fichier dont nous souhaitons compter les mots sera traité ligne par ligne.
La fonction `compter_mots` sera donc appelée pour chaque ligne de texte contenu dans ce fichier.
Le comptage des mots de chaque ligne devra donc être ajouté à un comptage global grâce à la fonction `ajouter_dictionnaire` que vous allez implémenter :

!!! example "Exemple - Appel à la fonction `ajouter_dictionnaire`"

    ```
    >>> comptage_global = {}
    >>> ajouter_dictionnaire(comptage_global, compter_mots('hello, world'))
    >>> comptage_global
    {'hello': 1, 'world': 1}
    >>> ajouter_dictionnaire(comptage_global, compter_mots('hello, monde'))
    >>> comptage_global
    {'hello': 2, 'world': 1, 'monde': 1}
    ```

!!! note "Instructions - Implémentation de la fonction `ajouter_dictionnaire`"

    1. Ouvrez le fichier `main.py`
    2. Implémentez la fonction `ajouter_dictionnaire`
    3. Exécutez le fichier `main.py` pour tester votre implémentation. Celle-ci ne sera correcte que lorsque le *doctest* de la fonction `ajouter_dictionnaire` ne signalera plus d'erreur


### Comptage des mots d'un fichier

Nous souhaitons disposer d'une fonction `compter_mots_fichier` qui prend en paramètre un chemin de fichier et qui effectue les traitements suivants :

- Ouverture du fichier (fonction `open`)
- Lecture des lignes du fichier (fonction `readline`)
- Comptage des mots de chaque ligne du fichier (`compter_mots`)
- Renvoie d'un dictionnaire contenant le nombre d'occurrences de l'ensemble des mots du fichier

!!! note "Instructions - Implémentation de la fonction `compter_mots_fichier`"

    1. Ouvrez le fichier `main.py`
    2. Implémentez la fonction `compter_mots_fichier`
    3. Exécutez le fichier `main.py` pour tester votre implémentation. Celle-ci ne sera correcte que lorsque le *doctest* de la fonction `compter_mots_fichier` ne signalera plus d'erreur

!!! help "Aide - Lecture d'un fichier"

    ```python
    f = open("fichier.txt", "r", encoding="utf-8") # ouverture du fichier en lecture seule
    lignes = f.readlines()                         # lecture de toutes les lignes du fichier
    close(f)                                       # fermeture du fichier une fois l'ensemble des traitements terminés
    ```

### Les mots les plus utilisés (Bonus)

Nous souhaitons connaître les mots les plus utilisés d'un document texte.

!!! note "Instructions"

    1. Ouvrez le fichier `main.py`
    2. Appelez la fonction `compter_mots_fichier` sur le texte `les_miserables.txt`
    3. Affichez les 100 mots les plus utilisés d'au moins 3 caractères dans l'ordre décroissant<br>
       *:material-comment-alert: vous pouvez utiliser toute fonction ou méthode Python*

!!! help "Aide - Tri d'un tableau"

    Pour apprendre à trier un tableau, consultez la documentation suivante :

    - [:material-link: Fonction sorted](https://docs.python.org/fr/3/library/functions.html#sorted){:target="_blank"}
    - [:material-link: Guide pour le tri](https://docs.python.org/fr/3/howto/sorting.html#sortinghowto){:target="_blank"}