---
title: Projet 1 - Présentez-vous
description: Projet de création d'une page web de présentation 
---

# Présentez-vous

## Introduction

Ce projet consiste en la création d'un mini-site web composé de deux pages.
Une première page sera consacrée à vous, et une seconde à un ou plusieurs de vos centres d'intérêt.
Des contraintes techniques sont imposées et vous serez évalué sur le respect de celles-ci.

!!! success "Objectifs"

    - mesurer votre capacité à suivre des consignes
    - mesurer votre maîtrise des langages HTML et CSS
    - mesurer le soin apporté au code (usage approprié des balises et code syntaxiquement correct)
    - mieux vous connaître

!!! warning "Projet individuel"

    Ce projet est une réalisation personnelle.
    Vous pouvez partager vos connaissances et découvertes à vos camarades mais le partage de code est interdit.
    Toute similitude de code sera sanctionnée.

## Consignes

### Contraintes de contenus

Votre mini-site web ne doit comporter que **deux pages** dont voici les descriptions :

!!! info "Page d'accueil"

    - Page d'accueil du site, elle est dédiée à vous présenter 
    - Le code est enregistré dans un fichier nommé `index.html`
    - La page doit contenir au minimum les informations suivantes :
        - votre classe et année scolaire ;      
        - nom, prénom ;
        - une photo (un avatar ou vous-même) ;
        - vos spécialités ;
        - vos souhaits d'études supérieures et/ou de métier ;
        - vos centres d'intérets.
    - La page doit contenir un lien hypertexte pointant vers la seconde page du mini-site dédiée à la présentation d'un ou plusieurs centres d'intérêt

!!! info "Page des centres d'intérêt"

    - Seconde page dédiée à présenter un ou plusieurs de vos centres d'intérêt
    - Le code est enregistré dans un fichier dont le nom est libre mais cohérent avec le contenu de la page    
    - Le contenu est libre mais doit respecter la [legislation française](https://www.service-public.fr/particuliers/vosdroits/F32075) 
    - Un lien hypertexte doit permettre de retourner vers la page d'accueil 

### Contraintes d'organisation

Les fichiers de votre projet doivent être rangés dans un dosser à votre nom.
À l'intérieur de celui-ci doivent être présents :

- un dossier `css` pour y placer vos fichiers CSS ;
- un dossier `images` pour les fichiers des images présentes sur votre mini-site ;
- vos deux fichiers HTML.

!!! info "Aperçu de l'arborescence de dossiers et de fichiers"

    ```
    nom_prenom_siteweb
    ├── css
    │   └── style.css
    ├── images
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    ├── index.html
    └── ???.html
    ```

!!! warning "Tout en minuscules"
    
    Veillez à ce que vos noms de fichiers et de dossiers soient en minuscules.
    Tout devrait bien fonctionner bien sous Windows ou MacOS.
    Cependant, certains systèmes d'exploitation comme Linux ont un système de fichiers sensible à la casse (qui distingue les minuscules des majuscules).
    
    En cas de sensibilité à la casse, avoir des images stockées dans le dossier `Images/...` et les appeler en HTML avec le chemin `images/...` provoquera une anomalie.
    


??? example "Exemple d'arborescence"

    Je suis [Tim Berners-Lee](https://fr.wikipedia.org/wiki/Tim_Berners-Lee){:target="_blank"} l'inventeur du web. 
    Je souhaite créer un mini-site pour me présenter et décrire les langages du web. 
    Voici l'arborescence des dossiers et fichiers de mon projet :
    
    ```
    tim_berners_lee_siteweb
    ├── css
    │   └── style.css
    ├── images
    │   ├── logo-html.jpg
    │   ├── logo-css.jpg
    │   └── exemple-code.png
    ├── index.html
    └── langages-web.html
    ```

### Contraintes de code HTML

Vous êtes libres d'utiliser tous les éléments HTML que vous jugerez nécessaires.
Cependant, vous devez obligatoirement utiliser les éléments de la liste suivante :

!!! info "Éléments HTML obligatoires"

    | Élément                          | Balises                                                    | Commentaire                                                                                                                                     |
    |:---------------------------------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
    | Titre principal                  | `#!html <h1></h1>`                                         | Un seul par page.<br />Présent sur les deux pages                                                                                               |
    | Sous-titre                       | `#!html <h2></h2>`                                         |                                                                                                                                                 |
    | Paragraphe                       | `#!html <p></p>`                                           |                                                                                                                                                 |
    | Fort ou emphase                  | `#!html <strong></strong>` ou `#!html <em></em>`           | L'un ou l'autre                                                                                                                                 |
    | Image                            | `#!html <img src="" alt="">`                               | N'oubliez pas l'attribut `alt`.<br/>Pas d'images externes. Toutes les images doivent être enregistrées dans le dossier `images`                 |
    | Lien hypertexte                  | `#!html <a href="url"></a>`                                | N'oubliez pas la navigation entre les deux pages.<br/>Vous devez avoir au moins un lien sortant (pointant vers un site web autre que le vôtre). |
    | Liste à puces ou liste numérotée | `#!html <ul><li></li></ul>` ou `#!html <ol><li></li></ol>` | L'un ou l'autre                                                                                                                                 |
    | Tableau                          | `#!html <table></table>`                                   |                                                                                                                                                 |
    | Titre                            | `#!html <title></title>`                                   | Présent sur les deux pages                                                                                                                      |
    | Métadonnée description           | `#!html <meta name="description" content="...">`           | Présent sur les deux pages. Description de votre page à saisir dans l'attribut `content`                                                        |
    | Liens vers une ressource CSS     | `#!html <link rel="stylesheet" href="">`                   | Présent sur les deux pages                                                                                                                      | 

??? tip "Code HTML de base d'une page web"

    Pour rappel, voici le code HTML minimal permettant la création d'une page web :

    ```html
    <!doctype html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>Titre de la page</title>
    </head>
    <body>
        Contenu de la page
    </body>
    </html>
    ```


### Contraintes de code CSS

Vous êtes libres d'utiliser toutes les propriétés CSS que vous jugerez nécessaires.
Cependant, vous devez obligatoirement faire usage des sélecteurs et propriétés listés ci-après.

!!! info "Sélecteurs CSS obligatoires"

    | Sélecteur           | Syntaxe                    | Commentaire                                                                                                             |
    |:--------------------|:---------------------------|:------------------------------------------------------------------------------------------------------------------------|
    | Sélecteur de balise | `#!css p { ... }`          |                                                                                                                         |
    | Sélecteur de classe | `#!css .ma-classe { ... }` | Ne pas oublier le `.` devant le nom de la classe.<br/>S'applique à toute balise ayant l'attribut `#!html class="ma-classe"` |

!!! info "Propriétés CSS obligatoires"

    | Propriété           | Syntaxe             | Commentaire                                  |
    |:--------------------|:--------------------|:---------------------------------------------|
    | Couleur du texte    | `#!css color:`      |                                              |
    | Couleur du fond     | `#!css background:` |                                              |
    | Alignement du texte | `#!css text-align:` | Pour centrer du texte ou des images          |
    | Largeur             | `#!css width:`      | À utiliser pour fixer la largeur des images. |

!!! warning "Feuille de style unique"
    
    **Attention**, vous n'avez droit qu'à un seul fichier CSS pour mettre en forme votre mini-site.
    À vous de définir astucieusement vos sélecteurs CSS afin que certains styles ne s'appliquent qu'à l'une ou l'autre des pages.

### Contraintes de qualité

Les langages HTML et CSS sont très permissifs. Pour s'assurer de la qualité de votre code, voici les contraintes de
qualité à respecter pour chacun d'eux :

!!! info "Qualité du code"

    === "Langage HTML"

        - Le code HTML de chaque page web doit être indenté de façon à ce qu'on puisse bien identifier l'ouverture et la fermeture des balises
        - Le code HTML devra être vérifié en chargeant vos pages sur le site [W3C Markup Validation Service](https://validator.w3.org/#validate_by_upload+with_options). Elles ne devront comporter aucune erreur
        - Si vous avez l'anomalie *<< Trailing slash on void elements has no effect and interacts badly with unquoted attribute values >>*, supprimez le `/` de fin des balises auto-fermantes (`meta`, `link`, `ìmg`, ...)

    === "Langage CSS"

        - Le code CSS devra être vérifié en chargeant vos fichiers de style sur le [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/#validate_by_upload). Ils ne devront comporter aucune erreur

## Envoi du projet

Votre projet sera à déposer dans Pronote selon la date annoncée par votre enseignant. Les contraintes à respecter sont
les suivantes :

- l'ensemble de votre projet doit être compressé au format ZIP ; 
- le poids du fichier ZIP ne doit pas dépasser 4 Mo ;
- le nom du fichier ZIP est libre.

??? tip "Création d'un fichier ZIP"

    === "Windows 11"

        1. Lancez l'explorateur de fichiers
        2. Retrouvez le dossier à compresser au format ZIP
        3. Cliquez avec le bouton droit sur le dossier à compresser
        4. Choisir l'option **Compresser dans le fichier ZIP**

    === "Windows 10"

        1. Lancez l'explorateur de fichiers
        2. Retrouvez le dossier à compresser au format ZIP
        3. Cliquez avec le bouton droit sur le dossier à compresser
        4. Choisir l'option **Envoyer vers** puis **Dossier compressé**