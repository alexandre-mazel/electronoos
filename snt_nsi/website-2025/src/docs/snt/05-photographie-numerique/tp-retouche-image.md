---
description: Retouche d'une image
source: https://www.pedagogie.ac-nantes.fr/enseignements-informatiques/enseignement/snt/luminosite-et-contraste-1213044.kjsp?RH=PEDA
---

# Retouche d'une image

## Introduction

Ces travaux pratiques ont pour objectif de faire comprendre les concepts relatifs à la luminosité des pixels et
effectuer des retouches.

!!! danger "Travail à rendre"

    Un compte rendu sera à rédiger et à déposer sur Pronote en fin de séance.

## Préparation

### Espace de travail

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'application <i class="icon file-explorer"></i> **Explorateur de fichiers**
        2. Dans le dossier `Document`, s'il n'y a pas de dossier `SNT`, créez-le
        3. Dans le dossier `SNT`, s'il n'y a pas de dossier `Photographie`, créez-le
        4. Dans le dossier `Photographie`, créez-le dossier `TP2 - Retouche`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier `SNT`, créez-le
        3. Dans le dossier `SNT`, s'il n'y a pas de dossier `Photographie`, créez-le
        4. Dans le dossier `Photographie`, créez-le dossier `TP2 - Retouche`

### Téléchargement

Pour réaliser ces travaux pratiques, il est nécessaire de disposer de certains fichiers.

!!! note "Récupération des fichiers"

    1. Téléchargez le fichier ZIP contenant les fichiers nécessaires : [:material-download: télécharger](assets/SNT05_TP2.zip){:download="SNT05_TP2.zip"}
    2. Ouvrez le fichier ZIP<br>*(si le navigateur ne l'ouvre automatiquement, cliquez sur le fichier téléchargé)*
    3. Sélectionnez tous les fichiers et dossiers  <span class="shortcut">++ctrl+a++</span>
    4. Copiez tous les fichiers et dossiers <span class="shortcut">++ctrl+c++</span>
    5. Collez les fichiers dans le dossier `SNT\Photographie\TP2 - Retouche` <span class="shortcut">++ctrl+v++</span>

    ??? help "Aide vidéo"

        <div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/fb39b9fdd7184179a05bab2c9534c088?sid=9fa4d6f6-2dac-4f83-aa3b-7e1add8dcc90" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>

### Compte rendu

Un compte rendu est à rédiger et à déposer sur Pronote au format PDF en fin de séance.

!!! note "Préparation du compte rendu"

    1. Créez un document texte en utilisant un logiciel de traitement de texte *(LibreOffice Writer, Microsoft Word, ...)*
    2. Ajoutez un titre, une date, votre classe, votre prénom et votre nom
    3. Enregistrez immédiatement le document dans le dossier `TP2 - Retouche`

## Caractéristiques d'une image

### Luminosité

Dans une image numérique, un niveau de gris représente la **luminosité d'un pixel**.
Un niveau de gris varie alors du noir *(la plus faible luminosité)* au blanc *(la plus forte luminosité)* avec un
certain nombre de nuances intermédiaires selon la **profondeur de couleurs** de l'image.

La profondeur de couleur est définie par le nombre de bits utilisés pour représenter chaque pixel.
Plus ce nombre est élevée, plus le nombre de nuances de gris sera grand.

|     Profondeur     |      Nombre de nuances      |             Aperçu              |
|:------------------:|:---------------------------:|:-------------------------------:|
|       3 bits       |  2<sup>3</sup> = 8 nuances  | ![3 bit](images/3bit_color.png) |
|       4 bits       | 2<sup>4</sup> = 16 nuances  | ![4 bit](images/4bit_color.png) |
|       5 bits       | 2<sup>5</sup> = 32 nuances  | ![5 bit](images/5bit_color.png) |
| 8 bits *(1 octet)* | 2<sup>8</sup> = 256 nuances | ![8 bit](images/8bit_color.png) |

!!! info "Information"

    Afin de simplifier les expérimentations de ces travaux pratiques, nous n'utiliserons que des images en noir et blanc.
    Celles-ci ont une profondeur de couleurs de 8 bits ce qui signifie qu'elles sont construites à partir de 256 nuances de gris.

### Histogramme

#### Principe

Un histogramme est un graphique qui indique le nombre de pixels dans l'image pour chaque valeur de luminosité.
Pour une profondeur de couleurs de 8 bits, les valeurs vont de 0 *(luminosité minimale)* à 255 *(luminosité maximale)*.
Chaque pic correspond au nombre de pixels pour une de luminosité donnée. Plus il est haut, plus sont nombreux les pixels pour cette luminosité. 

<figure markdown>
![Histogramme de la Joconde](images/joconde_histogramme.png){:style="max-width:100%;"}
<p><em>Histogramme du portrait de Mona Lisa</em></p>
</figure>

!!! note "Activité 1"
    
    Observez l'histogramme de l'image de *La Joconde* et déduisez-en la luminosité globale de l'image *(claire, neutre ou sombre)*.
    Écrivez votre réponse dans le compte rendu **en justifiant**.

#### Construction d'un histogramme

Voici une image de 8x8 pixels de définition représentant un rectangle gris.
Celle-ci a une profondeur de couleurs de 8 bits, mais ses pixels n'ont finalement que 3 nuances de gris sur les 256 possibles :

<div style="display:flex; margin:3em; justify-content:center; align-items: center; gap:50px;" markdown>
<div markdown>
![Histogramme](images/image_histogramme.png)
</div>
<div>
    <table>
        <tr><th style="text-align:center;">Nuance</th><th style="text-align:center;">Luminosité</th></tr>
        <tr><td style="text-align:center;"><div style="display:inline-block;width:20px;height:20px;border:1px solid black;background:black;"></div></td><td style="text-align:center;">0</td></tr>
        <tr><td style="text-align:center;"><div style="display:inline-block;width:20px;height:20px;border:1px solid black;background:#969696;"></div></td><td style="text-align:center;">150</td></tr>
        <tr><td style="text-align:center;"><div style="display:inline-block;width:20px;height:20px;border:1px solid black;background:white;"></div></td><td style="text-align:center;">255</td></tr>
    </table>
</div>
</div>


!!! note "Activité 2"

    Construire l'histogramme correspondant à l'image ci-dessus. Pour cela :

    1. Accédez au dossier `SNT\Photographie\TP2 - Retouche\histogramme_construction`
    2. Complétez le fichier `SNT05_histogramme.ods` en indiquant dans la colonne **Nombre de pixels**, le nombre de pixels que contient l'image pour chaque luminosité
    3. Faites une capture d'écran de l'histogramme obtenu  <span class="shortcut">++win+shift+s++</span>
    4. Collez la capture dans votre compte rendu

    ??? help "Aide vidéo"
        
        Exemple pour une image contenant 60 pixels noirs (intensité de 0) et 4 pixels gris (intensité de 150) :

        <div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/8fbaf0b9522648b89ddb657d3f511280?sid=962af908-8d4c-4a3d-9b24-6c54bc410691" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>

#### Interprétation

Le dossier `histogramme_interpretation` comporte 3 images et 3 histogrammes :

<figure markdown>
![Histogrammes](images/histogrammes.png){:style="max-width:100%;"}
</figure>

!!! note "Activité 3"
    - Visualisez les images et les histogrammes depuis le dossier `histogramme_interpretation`
    - Associez chaque histogramme à la bonne image. Vous répondrez en faisant des phrases :<br>
    *"L'histogramme numéro ... correspond à celui de l'image ... car ..."*

!!! note "Activité 4"

    Lancez une application de retouche d'image et vérifiez les histogrammes de chaque image. Vous pouvez utiliser au choix :

    - [:material-link: Pixlr](https://pixlr.com/fr/editor/){:target=_blank} *(application en ligne)* : Ajustement ▶ Niveaux...
    - Gimp *(uniquement sur les ordinateurs du lycée)* : Couleurs ▶ Niveaux...

## Traitement d'image


### La courbe tonale

La courbe tonale est un outil proposé par toute application de retouche d'image. Celui-ci permet d'ajuster la luminosité
des pixels.

#### Exemple

<figure markdown>
![Courbe tonale](images/joconde_courbe.png){:style="max-width:100%;"}
<p><em>Modification de la courbe tonale de La Joconde</em></p>
</figure>

#### Explication

L'axe des abscisses correspond à l'intensité lumineuse originale des pixels.
L'axe des ordonnées correspond à l'intensité lumineuse modifiée des pixels.
Sans modification, la courbe est une droite correspondant à *y = x*.
Il est possible de modifier manuellement cette courbe et ainsi faire varier *y* par rapport à *x*.

<figure markdown>
![Explication](images/explication_courbe_tonale.png){:style="max-width:50%;margin-left:auto;margin-right:auto;"}
<p><em>Exemple : tous les pixels d'intensité 100 prendront la valeur 200 après modifications. Ils vont donc s'éclaircir.</em></p>
</figure>

### Exposition

#### Principe

L'exposition est la quantité de lumière qui atteint le capteur de votre appareil photo.
Une forte exposition se traduit par une image lumineuse et inversement, une faible exposition se traduit par une image
plus sombre.
L'exposition peut être ajustée après la prise de vue en modifiant la courbe tonale.

#### Mise en pratique

Soit les courbes tonales suivantes :

<div style="display:flex;margin:1em;justify-content:center;align-items:center;gap:50px">
<div style="text-align:center">
<img src="../images/courbe_exposition_1.png" alt="Exposition 1">
<p><em>Courbe 1</em></p>
</div>
<div style="text-align:center">
<img src="../images/courbe_exposition_2.png" alt="Exposition 1">
<p><em>Courbe 2</em></p>
</div>
</div>

!!! note "Activité 5"

    Vous devez réussir à distinguer entre les deux courbes celle qui permet d'augmenter l'exposition et celle qui permet de la réduire.
    Pour cela, modifiez la courbe tonale d'une des images de ce TP et ajoutez une capture d'écran du résultat obtenu dans votre compte rendu et concluez.

    Pour modifier la courbe tonale, vous pouvez utiliser au choix :

    - [:material-link: Pixlr](https://pixlr.com/fr/editor/){:target=_blank} *(application en ligne)* : Ajustement ▶ Courbes...
    - Gimp *(uniquement sur les ordinateurs du lycée)* : Couleurs ▶ Courbes...

### Contraste

#### Principe

Le contraste correspond à la différence de luminosité entre les parties claires et les parties sombres d'une image.
Augmenter le contraste revient à égaliser l'histogramme : l'intensité est mieux répartie en "étalant" l'histogramme.

<figure markdown>
![Modification du contraste](images/contraste.png){:style="max-width:100%;margin-left:auto;margin-right:auto;"}
</figure>

#### Mise en pratique

Soit les courbes tonales suivantes :

<div style="display:flex;margin:1em;justify-content:center;align-items:center;gap:50px">
<div style="text-align:center">
<img src="../images/courbe_contraste_1.png" alt="Exposition 1">
<p><em>Courbe 1</em></p>
</div>
<div style="text-align:center">
<img src="../images/courbe_contraste_2.png" alt="Exposition 1">
<p><em>Courbe 2</em></p>
</div>
</div>

!!! note "Activité 6"

    Vous devez réussir à distinguer entre les deux courbes celle qui permet d'augmenter le contraste et celle qui permet de le réduire.
    Testez vos modifications sur une des images de ce TP, ajoutez une capture d'écran des résultats obtenus dans votre compte rendu et concluez.

    Pour modifier les courbes, vous pouvez utiliser au choix :

    - [:material-link: Pixlr](https://pixlr.com/fr/editor/){:target=_blank} *(application en ligne)* : Ajustement ▶ Courbes...
    - Gimp *(uniquement sur les ordinateurs du lycée)* : Couleurs ▶ Courbes...

    ??? help "Aide vidéo"
        
        Exemple de reproduction de la courbe 1 sous Pixlr

        <div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/5e1b6ab79b104423ad3fbd52f6986ec6?sid=80af98a8-d07c-4e6a-8342-698f1ffdc4b7" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>


## Envoi du travail

!!! note "Dépot du travail sur Pronote"

    1. Enregistrez votre compte rendu et exportez-le au **format PDF**
    1. Connectez-vous à l'ENT : [:material-link: https://ent.iledefrance.fr](https://ent.iledefrance.fr){:target="_blank"}
    3. Accédez à l'application **Pronote**
    4. Depuis l'accueil, recherchez le devoir **SNT05 - TP - Retouche d'une image**
    5. Cliquez sur le bouton <span class="pronote-button">Déposer ma copie</span>
    6. Cliquez sur le bouton **Un seul fichier (*.pdf, *.doc, ...)**
    7. Déposez votre fichier PDF