---
title: TP3 - Format JSON
description: Écriture d'un programme Python permettant le traitement de données au format JSON
---

# Format JSON

## Introduction

Le **JSON** *([:material-link: JavaScript Object Notation](https://www.json.org/json-fr.html){:target="_blank"})* est un format de représentation textuelle de structures de données dérivé du Javascript.
Il permet de représenter des dictionnaires, des tableaux, des booléens, des nombres et des chaînes de caractères.

L'objectif de ces travaux pratiques est d'écrire un programme permettant de charger et traiter des données au format JSON.

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
        4. Dans le dossier `chapitre_11` créez le dossier `tp3_format_json`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier `NSI`, créez-le
        3. Dans le dossier `NSI`, s'il n'y a pas de dossier nommé `chapitre_11`, créez-le
        4. Dans le dossier `chapitre_11` créez le dossier `tp3_format_json`

### Téléchargement des fichiers

Pour réaliser ces travaux pratiques, il est nécessaire de disposer de certains fichiers.

!!! note "Récupération des fichiers"

    1. Téléchargez le fichier ZIP contenant les fichiers nécessaires : [:material-download: télécharger](assets/NSI1RE11_TP3.zip){:download="NSI1RE11_TP3.zip"}
    2. Ouvrez le fichier ZIP<br>*(si le navigateur ne l'ouvre automatiquement, cliquez sur le fichier téléchargé)*
    3. Sélectionnez tous les fichiers et dossiers  <span class="shortcut">++ctrl+a++</span>
    4. Copiez tous les fichiers et dossiers <span class="shortcut">++ctrl+c++</span>
    5. Collez les fichiers dans le dossier `NSI\chapitre_11\tp3_format_json` <span class="shortcut">++ctrl+v++</span>

## Mise en pratique

### Analyse du fichier JSON

Le fichier `cinemas.json` provient du site [:material-link: data.gouv.fr](https://www.data.gouv.fr/fr/datasets/les-salles-de-cinema-en-ile-de-france/){:target="_blank"}.
Il contient les caractéristiques des cinémas franciliens au format JSON.

!!! note "Instructions - Analyse du fichier `cinemas.json`"

    1. Ouvrez le fichier `cinemas.json` avec l'application Bloc-notes ou tout autre éditeur de texte de votre choix
    2. Essayez de comprendre la structure du document

!!! question "Question"
    
    Quels types de données pouvez-vous distinguer dans le fichier `cinemas.json` ?

### Traitement du fichier JSON

Nous souhaitons maintenant appliquer des traitements sur les données JSON afin d'extraire des informations sur les cinémas d'Île-de-France.
L'ensemble du code devra être écrit dans le fichier `main.py`. Vous écrirez une fonction pour chaque point demandé.
Celle-ci prend en paramètre la structure JSON chargée à partir du fichier `cinema.json`.

!!! note "Instructions - Traitements à implémenter"

    1. Affichage du nombre de cinémas en Île-de-France
    2. Affichage de l'ensemble des descripteurs d'un cinéma *(ensemble des clés du champ `fields`)*
    3. Affichage du nom des cinémas de votre ville *(où ceux de la ville de Chelles s'il n'y en a pas)*
    4. Calcul du nombre total d'écrans et de fauteuils de cinéma dans toute l'Île-de-France
    5. Affichage du nom de tous les cinémas d'Art et Essai
    6. Affichage du nom du cinéma disposant du plus d'écrans *(bonus)*
