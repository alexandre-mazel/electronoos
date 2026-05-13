---
title: Le langage PHP
description: Installation de l'interpréteur PHP
---

# Le langage PHP

## Installation

!!! note "Téléchargement"

    1. Téléchargez [:material-download: PHP 8.3.7](https://windows.php.net/downloads/releases/php-8.3.7-nts-Win32-vs16-x64.zip)
    2. Décompressez le fichier ZIP
    3. Renommez le dossier `php-8.3.7-nts-Win32-vs16-x64` en `php`

!!! note "Configuration de la commande PHP"

    === "Invite de commandes"

        L'interpréteur PHP doit être lancé depuis une interface de ligne de commande.
    
        1. Lancez l'application **Invite de commandes**
        2. Configurez la variable de localisation des exécutables `PATH` en saisissant la commande suivante :
            ```bat
            set PATH=%PATH%;C:%HOMEPATH%\Downloads\php
            ```
        3. Vérifiez que l'exécutable `php.exe` soit bien dans le `PATH` en saisissant la commande suivante :
            ```bat
            php -v
            ```
        4. Vous devez obtenir l'affichage suivant :
            ```
            PHP 8.3.6 (cli) (built: Apr 10 2024 14:53:44) (NTS Visual C++ 2019 x64)
            Copyright (c) The PHP Group
            Zend Engine v4.3.6, Copyright (c) Zend Technologies
            ```
        5. Fermez la fenêtre ouverte

    === "Powershell"

        L'interpréteur PHP doit être lancé depuis une interface de ligne de commande.

        1. Lancez l'application **Powershell**
        2. Configurez la variable de localisation des exécutables `PATH` en saisissant la commande suivante :
            ```powershell
            $env:path += ";$env:userprofile\Downloads\php"
            ```
        3. Vérifiez que l'exécutable `php.exe` soit bien dans le `PATH` en saisissant la commande suivante :
            ```powershell
            php -v
            ```
        4. Vous devez obtenir l'affichage suivant :
            ```
            PHP 8.3.6 (cli) (built: Apr 10 2024 14:53:44) (NTS Visual C++ 2019 x64)
            Copyright (c) The PHP Group
            Zend Engine v4.3.6, Copyright (c) Zend Technologies
            ```
        5. Fermez la fenêtre

## Première page dynamique

!!! note "Création de la page"

    1. Dans votre dossier `NSI`, s'il n'y a pas de dossier nommé `chapitre_14`, créez-le
    2. Dans le dossier `chapitre_14` créez le dossier `demo_php`
    3. Dans le dossier `demo_php` créez le fichier `index.php` avec le contenu suivant :

    ```html+php
    <?php 
        if (isset($_GET['nom'])) {
            $nom = $_GET['nom'];
        }
        else {
            $nom = 'toi';
        }
    ?>
    <!DOCTYPE html>
    <html lang="fr">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>Première page dynamique</title>
      </head>
      <body>
        <p>
        <?php for ($i=0 ; $i<10 ; $i++) { ?>
            Bonjour <?php echo $nom ?> !<br>
        <?php } ?>
        </p>
      </body>
    </html>
    ```

!!! note "Lancement du serveur HTTP"

    Afin de lancer facilement le serveur, vous allez créez un script shell de démarrage

    1. Dans le dossier `demo_php` créez le fichier `serveur.bat` avec le contenu suivant :

    ```bat
    set PATH=%PATH%;C:%HOMEPATH%\Downloads\php
    php -S localhost:8080
    ```        
    
    2. Depuis l'explorateur de fichier, double-cliquez sur le fichier `serveur.bat` pour le lancer 
    3. Accédez à la page [:material-link: http://localhost:8080](http://localhost:8080){:target=_blank}
    4. Trouvez comment afficher votre nom (sans modifier au code PHP)