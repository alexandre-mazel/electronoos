---
title: La confidentialité
description: Savoir configurer son navigateur web
---

# La confidentialité

## Introduction

Ces travaux pratiques ont pour objectif de vous faire découvrir certains paramètres de configuration de votre navigateur
afin de modifier le moteur de recherche par défaut et contrôler les cookies.

!!! warning "Attention"

    Ces travaux pratiques ont été conçus pour les navigateurs ci-dessous.
    Vous êtes libres d'utiliser tout autre navigateur cependant, vous devrez seul retrouver les fonctionnalités requises 
    dans les différents exercices

    - Le navigateur **Firefox** créé par [:material-link: Mozilla](https://www.mozilla.org/fr/){:target="_blank"}, une fondation sans but lucratif
    - Le navigateur **Chrome** créé par la société [:material-link: Google](https://about.google/intl/ALL_fr/){:target="_blank"}
    - Le navigateur **Edge** créé par la société [:material-link: Microsoft](https://www.microsoft.com/fr-tn/){:target="_blank"}

## Préparation

### Espace de travail

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'application <i class="icon file-explorer"></i> **Explorateur de fichiers**
        2. Dans le dossier `Document`, s'il n'y a pas de dossier nommé `SNT`, créez-le
        3. Dans le dossier `SNT`, s'il n'y a pas de dossier `web`, créez-le
        4. Dans le dossier `web`, créez le dossier `Confidentialité`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier nommé `SNT`, créez-le
        3. Dans le dossier `SNT`, s'il n'y a pas de dossier `web`, créez-le
        4. Dans le dossier `web`, créez le dossier `Confidentialité`

### Téléchargement des fichiers

Pour effectuer ces travaux pratiques, il est nécessaire de télécharger certains fichiers :

!!! note "Récupération des fichiers"

    1. Téléchargez le document de comptre rendu : [:material-download: télécharger](assets/SNT02_TP_confidentialite.docx){:download="SNT02_TP_confidentialité.docx"}
    2. Déplacez le document dans le dossier `Confidentialité`
    3. Ouvrez le document afin de pouvoir répondre aux questions tout au long des travaux pratiques

## Les moteurs de recherche

### Identifier le moteur de recherche

Vous allez commencer par simplement faire le choix d'un navigateur web et effectuer une recherche sur le web.

!!! target "Objectifs"

    - Savoir faire la distinction entre le navigateur web et le moteur de recherche
    - Savoir identifier le navigateur web
    - Savoir identifier le moteur de recherche
    

!!! note "Instructions"
    
    1. Lancez le navigateur web de votre choix
    2. Effectuez une recherche quelconque depuis la **barre d'adresse**
    3. Répondez aux deux questions suivantes dans le document de compte rendu

!!! question "Questions"

    - Quel navigateur web utilisez-vous pour ces travaux pratiques ?
    - Avec quel moteur de recherche votre navigateur web a-t-il traité votre requête ?


### Changer de moteur de recherche

Il y a souvent confusion entre navigateur web et moteur de recherche.
Afin que vous puissiez faire clairement la distinction entre les deux, 
vous allez modifier le moteur de recherche utilisé par défaut par votre navigateur Web.

!!! target "Objectif"

    Comprendre que le moteur de recherche est un service indépendant du navigateur web.

!!! note "Instructions"

    1. Accédez aux paramètres du navigateur pour choisir **Qwant** comme moteur de recherche<br> 
       *(Consulter l'aide :material-lightbulb-on-outline: ci-après en suivant les instructions correspondant à votre navigateur)*
    2. Faites une recherche quelconque **depuis la barre d'adresse**<br>
       *(Cette fois-ci c'est Qwant qui doit avoir été appelé par votre navigateur web)*

!!! help "Changer de moteur de recherche pour Qwant"

    === ":material-firefox: Firefox"

        - Se rendre dans **Paramètres**
        - Se rendre dans **:material-magnify: Recherche**
        - Choisir **Qwant** pour **Moteur de recherche par défaut**

    === ":material-google-chrome: Chrome"

        <h5>Accès aux paramètres</h5>

        - Se rendre dans **:material-cog-outline: Paramètres**
        - Se rendre dans **:material-magnify: Moteur de recherche**<br>
          :material-alert: Qwant n'est pas proposé dans la liste des moteurs, il faut l'ajouter

        <h5>Ajout d'un nouveau moteur de recherche</h5>

        - Se rendre dans **Gérer les moteurs de recherche et la recherche sur les sites**
        - En face de **Recherche sur le site**, cliquer sur **Ajouter**
        - Saisir les informations suivantes :
        <table>
            <tbody>
                <tr><th>Moteur de recherche</th><td>`Qwant`</td></tr>
                <tr><th>Raccourci</th><td>`q`</td></tr>
                <tr><th>URL</th><td>`https://www.qwant.com/?q=%s`</td></tr>
            </tbody>
        </table>
        - Cliquer enfin sur :material-dots-vertical: en face de Qwant et choisir **utiliser par défaut**

    === ":material-microsoft-edge: Edge"
        
        - Se rendre dans **:material-cog-outline: Paramètres**
        - Se rendre dans **:material-lock-outline: Confidentialité, recherche et services**
        - Se rendre dans **Barre d'adresse et recherche** *(faire défiler jusqu'en bas pour voir l'entrée)*
        - Choisir **Qwant** pour **Moteur de recherche utilisé dans la barre d'adresses**

### Utilisation de vos données par les moteurs de recherche

Nous souhaitons comparer les moteurs de recherche Google et Qwant sur l'usage des données personnelles.
Pour celà, vous allez lire des extraits des règles de confidentialité rédigées par les entreprises 
propriétaires de ces moteurs. 

!!! target "Objectif"

    Comprendre la différence de philosophie entre les moteurs de recherche. 

!!! note "Instructions"

    1. Lisez les politiques de confidentialité de Google et Qwant ci-dessous
    2. Répondez aux trois questions dans le document de compte rendu

??? info "Google - Règles de confidentialité"

    *Les extraits ci-après proviennent tous de la page [Règles de confidentialité](https://policies.google.com/privacy?hl=fr#infocollect){:target="_blank"} du site officiel de Google.*

    <h3>Votre activité</h3>

    Nous collectons des informations relatives à votre activité au sein de nos services.
    Celles-ci nous permettent par exemple de vous recommander une vidéo YouTube susceptible de vous intéresser.
    Les informations relatives à votre activité que nous recueillons peuvent inclure les éléments suivants :

    - Les termes que vous recherchez.
    - Les vidéos que vous regardez.
    - Vos vues de contenu et d'annonces ainsi que vos interactions avec ces derniers.
    - Informations audio et vocales
    - L'activité relative aux achats.
    - Les personnes avec lesquelles vous communiquez ou partagez du contenu.
    - L'activité sur des applications et sites tiers qui utilisent nos services.
    - L'historique de navigation Chrome que vous avez synchronisé avec votre compte Google.
    
    Si vous utilisez nos services pour passer et recevoir des appels ou envoyer et recevoir des messages,
    nous sommes susceptibles de collecter des informations sur les appels et les messages, tels que votre numéro de téléphone,
    celui de l'émetteur, celui du destinataire, les numéros de transfert, l'adresse e-mail de l'émetteur et du destinataire,
    l'heure et la date des appels et des messages, la durée des appels, les données de routage,
    ainsi que les types et volumes d'appels et de messages.

    <h3>Informations relatives à votre position géographique</h3>

    Nous collectons des informations sur votre position lorsque vous utilisez nos services,
    car ces données nous permettent de proposer des fonctionnalités telles que des itinéraires,
    des résultats de recherche concernant des éléments à proximité, ainsi que des annonces en fonction de votre position générale.

    Votre position géographique peut être déterminée avec des degrés de précision différents à l'aide des éléments suivants :

    - GPS et autres données des capteurs de votre appareil
    - Adresse IP
    - Activité sur les services Google, comme vos recherches et les lieux auxquels vous ajoutez un libellé (domicile ou travail, par exemple)
    - Des informations relatives à des éléments à proximité de votre appareil, tels que des points d'accès Wi-Fi, des antennes-relais et des appareils sur lesquels le Bluetooth est activé

    <h3>Proposer des services personnalisés, notamment en matière de contenu et d'annonces</h3>

    Nous utilisons les informations que nous collectons pour personnaliser nos services en fonction de vous, notamment 
    pour vous proposer des recommandations, du contenu personnalisé et des résultats de recherche personnalisés. [...]

    En fonction de vos paramètres, nous pouvons également vous proposer des annonces personnalisées sur la base de vos centres d'intérêt.
    Par exemple, si vous recherchez "vélos tout-terrain", vous verrez peut-être des annonces pour des équipements sportifs sur YouTube.
    [...]

??? info "Qwant - Politique de Confidentialité"

    *Les extraits ci-après proviennent tous de la page [Politique de Confidentialité](https://about.qwant.com/legal/confidentialite/){:target="_blank"} du site officiel de Qwant.*

    <h3>Un moteur de recherche qui respecte votre vie privée</h3>
    Chez Qwant, nous ne savons pas qui vous êtes. Pas de ciblage, ni de conservation de votre historique de recherche : votre âge, votre sexe et vos centres d’intérêts n’appartiennent qu’à vous. A chaque requête, vous partez d’une page blanche.

    <h3>Un web ouvert et neutre à votre service</h3>
    En ne traçant pas nos utilisateurs, notre moteur de recherche vous propose une vision panoramique du web et vous garantit des résultats neutres, sans bulle de filtre. Il ne vous enferme pas dans vos certitudes. Vos recherches précédentes n’influenceront pas les prochaines !

    <h3>Une navigation sans publicité ciblée !</h3>
    Qwant ne place aucun cookie publicitaire sur votre navigateur. De cette façon, la publicité qui apparaitra dans votre navigation sera liée à vos mots clés de recherche, et non à votre profil utilisateur.

    <h3>Vos données ne sont pas une monnaie d’échange</h3>
    Il est commun d’entendre aujourd’hui que les données sont le nouvel « or noir ». Pas chez Qwant. Nous ne vendons pas vos données à des organismes tiers, à des fins publicitaires ou pour tout autre usage.

    <h3>Une alternative made in France qui applique la législation européenne</h3>
    Soucieux de respecter le cadre législatif français et européen, Qwant applique rigoureusement le RGPD. Nous respectons les droits fondamentaux, y compris celui du droit à l’oubli qui vous offre la possibilité d’obtenir l’effacement de vos données.

!!! question "Questions"

    - **En résumant**, quelles sont les données collectées par Google et comment le justifie-t-il ?
    - Quelles sont les données collectées par Qwant et comment le justifie-t-il ?
    - Quels avantages et inconvénients voyez-vous à utiliser l'un ou l'autre de ces moteurs de recherche ?

## Les cookies

Les cookies sont des informations que tout serveur web peut envoyer et stocker dans votre navigateur.
Ceux-ci peuvent aussi être modifiés ou ajoutés directement par votre navigateur.
Enfin, les cookies sont renvoyés au serveur lors de chaque requête HTTP.

!!! target "Objectif"

    Comprendre la perception qu'on les élèves des cookies.

!!! note "Instructions"

    - Répondez à la question ci-desous dans le document de compte rendu
    - Ne faites pas de recherche sur le web

!!! question "Question"

    Selon vos connaissances, quelle est l'utilité des cookies ? À quoi servent-ils lorsque vous naviguez sur le web ?

### Les cookies nécessaires

Les cookies sont généralement évoqués lorsqu'il s'agit de publicité. 
Cependant, ils se révèlent indispensables dans d'autres situations.

!!! target "Objectif"

    Faire l'expérience des cookies **nécessaires**, c'est-à-dire ceux sans lesquels un site web ne pourrait pas fonctionner.

!!! note "Instructions"

    - Connectez-vous à l'ENT : [:material-link: https://ent.iledefrance.fr](https://ent.iledefrance.fr/){:target="_blank"}
    - Consultez les cookies déposés par l'ENT<br>
      *(Consulter l'aide ci-dessous :material-lightbulb-on-outline: en suivant les instructions correspondant à votre navigateur)*

!!! help "Consulter les cookies"

    === ":material-firefox: Firefox"

        - Cliquer avec le bouton droit n'importe où sur la page et choisir **Inpecter**
        - Se rendre sur l'onglet **Stockage**
        - Cliquer sur **Cookies**

    === ":material-google-chrome: Chrome"

        - Cliquer sur l'icône :material-tune-variant: à gauche de la barre d'adresse
        - Se rendre dans **:material-cookie-outline: Cookies et données des sites**
        - Se rendre dans **Gérer les données des sites sur l'appareil**

    === ":material-microsoft-edge: Edge"

        - Cliquer sur l'icône :material-lock-outline: à gauche de la barre d'adresse
        - Cliquer sur **Cookies (... en cours d'utilisation)**

Vous devez observer qu'un cookie a été déposé pour le domaine `ent.iledefrance.fr`.
Essayons de découvrir pour quelle raison en observant les conséquences de sa suppression sur la navigation.

!!! note "Instructions"

    - Revenez à la fenêtre de consultation des cookies
    - Supprimez tous les cookies du domaine `ent.iledefrance.fr`
    - Rechargez la page et répondre aux deux questions ci-dessous

!!! question "Questions"

    - Quelle conséquence a eu la suppression des cookies ?
    - Quelle explication donneriez-vous à l'utilisation des cookies par l'ENT ?


### Les cookies tiers

!!! target "Objectif"

    Découvrir la multitude de cookies pouvant être déposés par un site et ses partenaires (cookies tiers).

!!! note "Instructions"

    - Rendez-vous sur le site [:material-link: www.lemonde.fr](https://www.lemonde.fr){:target="_blank"}
    - Il vous sera proposé d'accepter l'utisation des cookies. Cliquez sur **Accepter et continuer**
    - Consultez les cookies présents sur le site
    - Répondez à la question ci-après

Vous devriez observer la présence de beaucoup plus de cookies. Vous êtes sur le site dont le nom de domaine est `monde.fr`.
Les cookies n'appartenant pas à ce domaine sont appelés des **cookies tiers**.
Ces cookies sont généralement utilisés pour suivre votre activité pour des raisons statistiques,
pour la personnalisation des contenus ou pour la publicité ciblée.

!!! question "Question"

    Donnez un exemple de cookie tiers déposé sur le site web du journal Le Monde

### Contrôler les cookies

Vous pouvez contrôler la présence des cookies tiers de plusieurs façons :

- Les refuser lorsqu'un site vous présente sa fenêtre de **préférences sur les cookies**
- Supprimer tous les cookies d'un site précis
- Supprimer tous les cookies de votre navigateur
- Modifier les paramètres relatifs à la confidentialité de votre navigateur

Vous allez modifier les paramètres de confidentialité de votre navigateur et observer les résultats sur le site 
[www.lemonde.fr](https://www.lemonde.fr){:target="_blank"}.

!!! target "Objectif"

    Savoir qu'il est possible d'ajuster le niveau de confidentialité d'un navigateur web et ainsi refuser automatiquement certains cookies.

!!! note "Instructions"

    - Modifiez les paramètres de confidentialité<br>
      *(Consulter l'aide ci-dessous :material-lightbulb-on-outline: en suivant les instructions correspondant à votre navigateur)*
    - Rafraichissez la page [:material-link: www.lemonde.fr](https://www.lemonde.fr){:target="_blank"}
    - Consultez les cookies présents sur le site<br>
      (Si vous utilisez **Firefox** cliquez cette-fois sur le :material-shield-outline: de la barre d'adresse)
    - Répondez aux questions ci-après

!!! help "Modifier les paramètres de confidentialité"

    === ":material-firefox: Firefox"

        - Se rendre dans **Paramètres**
        - Se rendre dans **:material-lock-outline: Vie privée et sécurité**
        - Choisir **Stricte** comme **Protection renforcée contre le pistage**

    === ":material-google-chrome: Chrome"

        - Se rendre dans **:material-cog-outline: Paramètres**
        - Se rendre dans **:material-security: Confidentialité et sécurité**
        - Choisir de **Bloquer les cookies tiers** en tant que **comportement par défaut**

    === ":material-microsoft-edge: Edge"

        - Se rendre dans **:material-cog-outline: Paramètres**
        - Se rendre dans **:material-lock-outline: Confidentialité, recherche et services**
        - Choisir **Stricte** comme **Protection contre le suivi**


!!! question "Questions"

    - Qu'observez-vous au niveau des cookies après avoir modifié les paramètres du navigateur ?
    - Souhaiteriez-vous être moins pisté par les sites web ? Si oui, pour quelle raison ?
    - La politique de confidentialité de Qwant évoque « une vision du Web sans bulle de filtre ».<br>
      Qu'est-ce qu'une **bulle de filtre** et voyez-vous un danger à ce phénomène ?<br>
      *(vous pouvez effectuer une recherche sur le Web et ne faites pas de copier/coller pour répondre)*


## Envoi du document

### Export au format PDF

Exportez votre document vers le format PDF en suivant les instructions correspondant au logiciel de traitement de texte
utilisé.

!!! note "Export au format PDF"

    === "Word"

        - Enregistrer le document via la fonction **Enregistrer sous...**
        - Choisir le format de fichier **PDF** au lieu de *Document Word (.docx)*

    === "LibreOffice"

        - Cliquer sur l'entrée **Fichier** de la *barre de menus*
        - Choisir l'option **Exporter vers > Exporter directement au format PDF**

### Dépôt du travail

!!! note "Dépôt d'une copie sur Pronote"

    1. Connectez-vous à l'**ENT** : [:material-link: https://ent.iledefrance.fr](https://ent.iledefrance.fr){:target="_blank"}
    2. Accédez à l'application **Pronote**
    3. Un *travail à faire* en SNT a été créé par votre enseignant. Il est identifiable sur la page d'accueil par un bouton :<br /> 
       **Déposer ma copie**{:style="display:inline-block;color:#4a1b7f;background-color:#ebdbff;padding:5px 20px;border-radius:10px;"}
    4. Cliquez sur le bouton **Déposer ma copie**
    5. Cliquez sur le bouton **Un seul fichier (*.pdf, *.doc, ...)**