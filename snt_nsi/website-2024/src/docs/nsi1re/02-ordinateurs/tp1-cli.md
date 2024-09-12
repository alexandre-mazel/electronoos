---
title: Chapitre 2 - Ordinateurs - TP1 Interpréteur de commandes
description: Découverte des interpréteurs de commande
---

# Interpréteur de commandes

## Introduction

Dans tout système d'exploitation, il existe une application appelée *« terminal »* ou *« console »*, et qui permet
d'exécuter des tâches en écrivant des commandes au clavier. Le terminal se présente généralement sous la forme d'une
simple fenêtre où un curseur clignotant signale l'attente d'une saisie de l'utilisateur.

!!! success "Objectif"

    Ces travaux pratiques ont pour objectif la découverte des commandes de base de l'interpréteur de commandes Linux 
    (en anglais **CLI** pour **command-line interpreter**).


## Préparation

### Lancement de Linux

Le programme officiel impose de connaître les commandes Linux.
Vos ordinateurs fonctionnant sous Windows, il est nécessaire de trouver un CLI fonctionnant sous Linux.
Pour cela, il existe des émulateurs Linux en ligne.

!!! note "Lancement d'un CLI Linux en ligne"

    1. Lancez un navigateur Web
    2. Connectez-vous à l'adresse [https://bellard.org/jslinux](https://bellard.org/jslinux){:target="_blank"}
    3. Identifiez la version **x86 Alpine Linux 3.12.0 Console**
    4. Cliquez sur **click here** pour lancer l'émulation

### ️Liste des commandes

Les commandes utilisables dans l'interpréteur sont innombrables et dépendent des applications installées sur votre système d'exploitation.

Voici une liste de commandes communément utilisées pour explorer et manipuler un système de fichiers.
Parcourez attentivement cette liste et comprenez le rôle de chaque commande avant de commencer les travaux pratiques.

| Commandes                      | Documentation                                                |
|:-------------------------------|:-------------------------------------------------------------|
| `pwd`                          | Affiche le chemin absolu du dossier courant                  |
| `ls`                           | Liste le contenu du dossier courant                          |
| `cat` *nom_fichier*            | Affiche le contenu du fichier *nom_fichier*                  |
| `cp` *source destination*      | Copie le fichier *source* dans *destination*                 |
| `mv` *source destination*      | Déplace et/ou renomme le fichier *source* vers *destination* |
| `rm` *nom_fichier*             | Supprimer le fichier *nom_fichier*                           |
| `cd` *nom_dossier*             | Place l'utilisateur dans le dossier *nom_dossier*            |
| `cd ..`                        | Place l'utilisateur dans le dossier parent                   |
| `mkdir` *nom_dossier*          | Crée un dossier nommé *nom_dossier*                          |
| `rmdir` *nom_dossier*          | Supprime le dossier *nom_dossier*                            |
| `chmod` *droits* *nom_fichier* | Modification des *droits* d'accès du fichier *nom_fichier*   |
| `man` *commande*               | Affiche la documentation d'une commande                      |

## Instructions

### Déplacements

!!! note "Déplacement dans une arborescence"

    1. Placez-vous à la racine `/`
    2. Placez-vous dans le dossier `root`
    3. Comment auriez-vous pu faire ça en une seule étape ?
    4. Listez le contenu du dossier `root`
    5. Listez le contenu du dossier `root` avec l'option `-al`

!!! tip "Conseil"
    
    Vous pouvez à tout moment utiliser la touche ++tab++ pour compléter la saisie d'un nom de fichier ou de répertoire.

### Création d'éléments

!!! note "Création de dossiers"

    1. Placez-vous dans le dossier `/home`
    2. Créez un dossier nommé `premiere_nsi`
    3. Dans ce dossier, créez un dossier nommé `chapitre_1`

!!! note "Création d'un fichier"

    1. Placez-vous dans le dossier `/home`
    2. Entrez la commande suivante :
    ```bash
    echo Hello, World! > salutations.txt
    ```
    3. Listez le contenu du dossier `home`. Un fichier nommé `salutations.txt` doit être maintenant présent
    4. Affichez le contenu du fichier `salutation.txt`

### Modification d'éléments

!!! note "Déplacement d'un fichier"

    1. Déplacez le fichier `salutations.txt` dans le dossier `chapitre_1`<br>
       *(Soyez rigoureux sur la saisie du chemin de destination car si le dossier n'existe pas, il pourrait y avoir renommage au lieu de déplacement)* 
    2. Créez un dossier `archives` dans le dossier `premiere_nsi`
    3. Copiez le fichier `salutations.txt` dans le dossier `archives` en le renommant `salutations_v1.txt`

!!! note "Suppression d'un fichier et d'un dossier"

    1. Supprimez le fichier `salutations.txt` présent dans le dossier `chapitre_1`
    2. Supprimez le dossier `chapitre_1`

### Droits d'accès

!!! note "Modification des droits d'un fichier"

    1. Enlevez les droits en lecture au fichier `salutations_v1.txt` pour tous les utilisateurs en utilisant la commande `chmod`
    2. Vérifiez les droits du fichier en utilisant la commande `ls -l`
    3. Redonnez les droits en lecture au fichier `salutations_v1.txt` à votre utilisateur uniquement


## Conclusion

### Questionnaire

Afin de vérifier votre compréhension de ces travaux pratiques, veuillez répondre au questionnaire Pronote suivant :

!!! note "Questionnaire de vérification"

    1. Connectez-vous à l'**ENT** : [https://ent.iledefrance.fr](https://ent.iledefrance.fr){:target="_blank"}
    2. Accédez à l'application **Pronote**
    3. Depuis l'accueil, recherchez le QCM intitulé **NSI1RE02 - TP1 - Interpréteur de commandes**
    4. Cliquez sur le bouton 
       **Exécuter le QCM**{:style="display:inline-block;color:#4a1b7f;background-color:#ebdbff;padding:5px 20px;border-radius:10px;"}