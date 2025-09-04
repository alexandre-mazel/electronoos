---
title: Chapitre 3 - Bases de la programmation - TP2 Python en mode script
description: Découverte du langage Python à travers son mode script
---

# Python en mode script

## Introduction

L'objectif de ces travaux pratiques est d'utiliser Python en mode script.
Il ne s'agit plus d'interagir directement avec l'interpréteur Python, mais d'écrire votre programme dans un fichier texte.
L'interpréteur sera solliciter pour lire votre fichier et exécuter les instructions qu'il contient.

## Préparation

### Espace de travail

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'**explorateur de fichiers**
        2. Accédez au dossier **Documents**
        3. Créez un dossier nommé **NSI** *(s'il n'existe pas déjà)*
        4. Dans le dossier **NSI**, créez un dossier nommé **chapitre_03**

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans votre zone personnelle, créez un dossier nommé **NSI** *(s'il n'existe pas déjà)*
        3. Dans le dossier **NSI**, créez un dossier nommé **chapitre_03**

### Environnement de développement

Pour ces travaux pratiques, l'utilisation de **Thonny** est **obligatoire**. 
Cet IDE a été conçu pour l'apprentissage du langage Python.

*[IDE]: Intergrated Development Environment

!!! note "Téléchargement de Thonny"

    Thonny devrait normalement être déjà installé sur votre ordinateur portable.
    Si ce n'est pas le cas ou si vous utilisez un ordinateur fixe du lycée, voici les instructions pour l'installer :
    
    1. Rendez vous sur le [site officiel](https://thonny.org/){:targer="_blank"}
    2. Approchez la souris de *« Windows »* dans la zone de téléchargement
    3. Téléchargez la version *« Portable variant with 64-bit Python 3.10 »*
    4. Décompressez l'archive ZIP téléchargée
    5. Déplacez le dossier décompressé dans votre dossier **Documents**
    6. Lancez Thonny en double-cliquant sur l'exécutable `Thonny.exe`

!!! danger "Ne perdez pas de temps !"
    
    Thonny peut être long à télécharger et décompresser.
    Ne perdez pas de temps et commencez immédiatement les travaux pratiques en utilisant l'interpréteur Python en ligne [Basthon](https://console.basthon.fr/){:target="_blank"}.
    Une fois Thonny prêt, lancez-le.

## Calculateur d'âge

### Version 1 - Saisie et affichage

!!! abstract "Instructions"

    <h4>Description</h4>
    Écrire un programme qui demande à l'utilisateur de saisir son année de naissance et qui l'affiche.

    <h4>Décomposition</h4>

    1. Demande d'une saisie utilisateur avec pour message *« Indique ton année de naissance : »*
    2. Affichage du texte  *« Ton année de naissance est : »* suivit de l'année de naissance saisie

    <h4>Exemple d'affichage</h4>
    ```
    Indique ton année de naissance : 2000
    Ton année de naissance est 2000
    ```

??? tip "Aide - Obtenir une saisie utilisateur"
    
    En Python, la fonction `#!python input()` permet de lire des données saisies au clavier (*entrée standard* par défaut).
    Celles-ci sont renvoyées par la fonction sous forme d'une **chaîne de caractères**.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html#input){:target="_blank"}

    !!! example "Exemple"
        
        === ":material-console: Console"

            ```
            >>> nom = input("Quel est ton nom ? ")
            Quel est ton nom ? Jean
            >>> nom
            'Jean'
            ```

        === ":material-file-document-edit-outline: Fichier"

            ```python
            nom = input("Quel est ton nom ? ")
            print(nom)
            ```

??? tip "Aide - Afficher une chaîne de caractères"

    En Python, la fonction `#!python print()` permet d'afficher du texte à l'écran (*sortie standard* par défaut).
    Chaque argument transmis à la fonction est automatiquement converti en chaîne de caractères.
    Ils sont ensuite affichés à l'écran séparés par un caractère d'espacement.
    
    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html#print){:target="_blank"}

    !!! example "Exemples"
        
        === "Avec plusieurs arguments"

            Voici un exemple d'appel de la fonction `print()` avec cinq arguments :
    
            <h5>:material-file-document-edit-outline: Code</h5>
            
            ```python
            nom = "Jean"
            age = 20
            print("Bonjour", nom, "tu as", age, "ans")
            ```
            
            <h5>:material-console: Affichage console</h5>
            
            ```
            Bonjour Jean tu as 20 ans
            ```
        
        === "Avec un seul argument"

            Voici un autre exemple d'appel avec un seul argument.
            Cette fois, nous avons construit nous-même le texte à afficher en utilisant la concaténation.
            Noter qu'il est nécessaire de convertir manuellement certaines données en chaîne de caractères grâce à la fonction `str()`
    
            <h5>:material-file-document-edit-outline: Code</h5>

            ```python
            nom = "Jean"
            age = 20
            texte = "Bonjour " + nom + " tu as " + str(age) + " ans"
            print(texte)
            ```

            <h5>:material-console: Affichage console</h5>
            
            ```
            Bonjour Jean tu as 20 ans
            ```

??? success "Solutions"

    === "Solution 1"

        ```python
        annee = input("Indique ton année de naissance : ")
        print("Ton année de naissance est :", annee)
        ```

    === "Solution 2"

        ```python
        annee = input("Indique ton année de naissance : ")
        affichage = "Ton année de naissance est : " + annee 
        print(affichage)
        ```    

    === "Solution 3"

        ```python
        annee = input("Indique ton année de naissance : ")
        print("Ton année de naissance est : " + annee)
        ```


### Version 2 - Calcul de l'âge

!!! abstract "Instructions"

    <h4>Description</h4>
    Écrire un programme qui demande à l'utilisateur de saisir son année de naissance et qui affiche son âge.
    Bien entendu l'âge est approximatif, c'est celui que l'utilisateur a, ou aura, cette année.

    <h4>Décomposition</h4>

    1. Demande d'une saisie utilisateur avec pour message *« Indique ton année de naissance : »*
    2. Calcul de l'âge
    3. Affichage du texte  *« Tu as : »* suivit de l'age de l'utilisateur.

    <h4>Exemple d'affichage</h4>
    ```
    Indique ton année de naissance : 2000
    Tu as 23 ans.
    ```

??? tip "Aide - Conversion d'une chaîne de caractères en nombre"

    En Python, la fonction `#!python int()` permet de convertir une chaîne de caractères en nombre.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html#int){:target="_blank"}

    !!! example "Exemple *(console)*"
        ```
        >>> chaine = "2000"
        >>> chaine
        '2000'
        >>> int(chaine)
        2000
        ```

??? tip "Aide - Conversion d'un nombre en chaîne de caractères"

    En Python, la fonction `#!python str()` permet de convertir un nombre en chaîne de caractères.
    Il est nécessaire de convertir un nombre en chaîne de caractères si on souhaite le concaténer à une autre chaîne.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html#func-str){:target="_blank"}

    !!! example "Exemple *(console)*"
        ```
        >>> nombre = 2000
        >>> nombre
        2000
        >>> str(nombre)
        '2000'
        ```

??? tip "Aide - Obtenir l'année courante *(hors programme)*"

    Pour les perfectionnistes, vous pouvez obtenir l'année courante en utilisant le module `datetime`.

    !!! example "Exemple"
        === ":material-console: Console"

            ```
            >>> from datetime import date
            >>> date.today().year
            2023
            ```

        === ":material-file-document-edit-outline: Fichier"

            ```python
            from datetime import date
            annee_courante = date.today().year
            ```

??? success "Solutions"

    === "Solution 1"

        ```python
        annee = int(input("Indique ton année de naissance : "))
        age = 2023 - annee
        print("Tu as", age, "ans")
        ```

    === "Solution 2"

        ```python
        annee = input("Indique ton année de naissance : ")
        age = 2023 - int(annee)
        print("Tu as", age, "ans")
        ```

    === "Solution 3"

        ```python
        annee = input("Indique ton année de naissance : ")
        print("Tu as", 2023 - int(annee), "ans")
        ```

    === "Solution 4"

        ```python
        annee = input("Indique ton année de naissance : ")
        age = 2023 - int(annee)
        affichage = "Tu as " + str(age) + " ans"
        print(affichage)
        ```    

    === "Solution 5"

        ```python
        annee = input("Indique ton année de naissance : ")
        print("Tu as " + str(2023 - int(annee)) + " ans")
        ```




### Version 3 - Mineur ou majeur

!!! abstract "Instructions"

    <h4>Description</h4>
    Écrire un programme qui demande à l'utilisateur de saisir son année de naissance et qui affiche son âge.
    Si l'individu est mineur, le programme affiche en supplément l'année à laquelle il deviendra majeur.

    <h4>Exemples d'affichage</h4>
    ```
    Indique ton année de naissance : 2000
    Tu as 22 ans et tu es majeur(e)
    ```

    ```
    Indique ton année de naissance : 2010
    Tu as 13 ans et tu es mineur(e)
    Tu seras majeur(e) en 2027
    ```

??? tip "Aide - Les structures conditionnelles"

    Voici un rappel de la syntaxe des structures conditionnelles en Python.

    [:material-file-document: Voir le tutoriel](https://docs.python.org/fr/3.8/tutorial/controlflow.html#if-statements){:target="_blank"}<br/>
    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html#input){:target="_blank"}
    
    !!! example "Exemples"
        === "if"
    
            ```python
            if x > 0:
                texte = "x est strictement positif"
            ```
    
        === "if-else"    
    
            ```python
            if x > 0:
                texte = "x est strictement positif"
            else:
                texte = "x est négatif ou nul"
            ```
        
        === "if-elif-else"
    
            ```python
            if x > 0:
                texte = "x est strictement positif"
            elif x == 0:
                texte = "x est nul"
            else:
                texte = "x est strictement négatif"
            ```

### Version 4 - Vérification de la saisie

!!! abstract "Instructions"

    <h4>Problème</h4>

    Le programme n'effectue actuellement aucune vérification de la saisie de l'utilisateur ce qui entrainer certains problèmes :
    
    - la saisie d'une année supérieure à l'année en cours entraine l'affichage d'âges négatifs;
    - la saisie de valeurs non numériques provoque une anomalie.

    <h4>Description</h4>
    
    Modifiez le programme de façon à ce que celui-ci s'interrompt si :
    
    - année saisie > 2022
    - année saisie < 1900
    - année saisie n'est pas une valeur numérique

    <h4>Exemples d'affichage</h4>
    ```
    Indique ton année de naissance : 2040
    Erreur, saisir une année comprise entre 1900 et 2023
    ```
    
    ```
    Indique ton année de naissance : 850
    Erreur, saisir une année comprise entre 1900 et 2023
    ```
    
    ```
    Indique ton année de naissance : hello
    Erreur, saisir une année comprise entre 1900 et 2023
    ```

??? tip "Aide - Vérifier si une chaîne est numériques *(hors programme)*"

    Avant de convertir une chaîne de caractères en un nombre (`#!python int` ou `#!python float`), il est possible de vérifier au préalable que celle-ci ne contienne uniquement des caractères numériques.
    Ceci est possible grâce à la méthode `#!python isdigit()` associée au type `#!python str`.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/stdtypes.html?highlight=isdigit#str.isdigit){:target="_blank"}

    !!! example "Exemple *(console)*"
        ```
        >>> "12".isdigit()
        True
        >>> "douze".isdigit()
        False
        >>> "-12".isdigit()
        False
        >>> "10.5".isdigit()
        False
        >>> nombre = "12"
        >>> nombre.isdigit()
        >>> True
        ```

??? tip "Aide - Interrompre l'exécution d'un programme *(hors programme)*"

    Si votre programme se trouve dans un état impropre à la poursuite de son exécution, vous pouvez en forcer la fin grâce à la fonction `#!python exit()`.
    Celle-ci prend optionnellement en argument une chaîne de caractères correspondant au message à afficher.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/sys.html#sys.exit){:target="_blank"}

    !!! example "Exemple"
        ```python
        x = int(input("Saisir un nombre différent de zéro : "))
        if x == 0:
            exit("Erreur, x = 0")
        
        print("10 /", x, "=", 10/x)
        ```


## Les états physiques de l'eau

!!! abstract "Instructions"

    <h4>Description</h4>
    
    Nous souhaitons un programme qui, à partir de la saisie d'une valeur de température, indique l'état de l'eau comme suit :
    
    - gazeux si température >= 100
    - liquide si température < 100 et > 0
    - solide si température <= 0

    <h4>Exemples d'affichage</h4>

    ```
    Saisir une température : 120
    L'eau est à l'état gazeux
    ```
    
    ```
    Saisir une température : 10
    L'eau est à l'état liquide
    ```
    
    ```
    Saisir une température : -10
    L'eau est à l'état solide
    ```

!!! warning "Attention"
    
    - Il n'est pas nécessaire de vérifier la saisie de l'utilisateur pour cet exercice
    - Pour celles et ceux qui les connaissent, ne pas utiliser les opérateurs booléens `not`, `and` et `or`

??? success "Solution"

    ```python
    temperature = int(input("Saisir une température : "))
    
    if temperature >= 100:
        print("L'eau est à l'état gazeux")
    elif temperature <= 0:
        print("L'eau est à l'état solide")
    else:
        print("L'eau est à l'état liquide")
    ```


## Le nombre secret

!!! success "Objectif"
    
    Nous souhaitons recréer en Python le jeu consistant à deviner un nombre choisi aléatoirement entre 0 et 100.

### Version 1 - Obtenir une valeur aléatoire

Écrire un programme stockant en mémoire un entier aléatoire compris entre 0 et 100 et l'affichant à l'écran.
La valeur choisie par l'ordinateur est affichée pour des raisons de débogage.
Celle-ci devra être masquée une fois le développement du jeu terminé.

??? tip "Aide - Obtenir un entier pseudo-aléatoire"

    Il est possible d'obtenir un entier aléatoire grâce à la fonction `randint()` du module `random`.
    Ci-dessous, un exemple d'appel de la fonction `randint()` pour obtenir un entier aléatoire  $n$ tel que $1 \leq n \leq 6$.

    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/random.html?highlight=randint#random.randint){:target="_blank"}

    !!! example "Exemple *(console)*"
        ```
        >>> import random
        >>> random.randint(1, 6)
        4
        >>> random.randint(1, 6)
        1
        >>> random.randint(1, 6)
        2
        >>> random.randint(1, 6)
        6
        ```

### Version 2 - Obtenir le choix du joueur

Modifier le programme de manière à demander à l'utilisateur de saisir un nombre.
La saisie devra se répéter tant que le joueur n'a pas trouvé le nombre aléatoire conservé en mémoire.
Les indications *« Plus petit »* ou *« plus grand »* seront affichées après chaque saisie pour guider le joueur.

!!! example "Exemple d'exécution"

    ```
    42
    Saisir un nombre : 10
    Plus grand
    Saisir un nombre : 50
    Plus petit
    Saisir un nombre : 42
    Bravo !
    ```

??? tip "Les boucles non bornées"

    Rappel de la syntaxe Python des boucles **while**, ou **boucles non bornées**.

    [:material-file-document: Voir le tutoriel](https://docs.python.org/fr/3.8/tutorial/introduction.html#first-steps-towards-programming){:target="_blank"}<br/>
    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/reference/compound_stmts.html?highlight=while#while){:target="_blank"}

    !!! example "Exemple"
        ```python
        # Affichage des entiers de 1 à 10.
        i = 1
        while i <= 10:
            print(i)
            i = i + 1
        ```

??? success "Solution partielle"

    Compléter la solution en remplaçant les `...` par le code adéquat :

    ```python
    import random
    
    nombre_secret = random.randint(..., ...)
    nombre_utilisateur = -1
    
    # Debug
    #print(nombre_secret)
    
    while nombre_utilisateur != ...:
        nombre_utilisateur = int(input('Saisir un nombre : '))
        
        if nombre_utilisateur > nombre_secret:
            print(...)
        elif ...:
            print("Plus grand")
            
    print("Bravo !")
    ```


### Version 3 - Affiner les messages

Modifier le programme de manière à apporter des indications supplémentaires à l'utilisateur s'il s'approche de l'entier à trouver :

- Si l'écart entre la valeur de l'utilisateur et celle à trouver est inférieure ou égale à 10, afficher *« tu chauffes ! »*
- Si l'écart entre la valeur de l'utilisateur et celle à trouver est inférieure ou égale à 2, afficher *« tu brûles ! »*

Le programme sera également modifié de manière à compter le nombre de tentatives et l'afficher à la fin du jeu.
Une fois, les développements terminés, ne plus afficher la valeur stockée en mémoire.

!!! example "Exemple d'exécution"

    Voici un exemple d'exécution si le nombre à trouver est 42 :
    
    ```
    Saisir un nombre : 10
    Plus grand
    Saisir un nombre : 60
    Plus petit
    Saisir un nombre : 50
    Plus petit, tu chauffes !
    Saisir un nombre : 40
    Plus grand, tu brûles !
    Saisir un nombre : 42
    Bravo ! Tu as trouvé en 5 tentatives
    ```

??? tip "Valeur absolue d'un nombre"

    La fonction Python permettant d'obtenir la valeur d'un nombre est `abs()`.
    
    [:material-file-document: Voir la documentation](https://docs.python.org/fr/3.8/library/functions.html?highlight=abs#abs){:target="_blank"}

    !!! example "Exemple *(console)*"
        ```
        >>> abs(-10)
        10
        >>> abs(10 - 12)
        2
        >>> abs(10 - 8)
        2
        ```

??? success "Solution"

    ```Python
    import random
    
    nombre_secret = random.randint(1, 100)
    
    # Debug
    # print(nombre_secret)
    
    # On initialise la proposition du joueur à -1
    # pour pouvoir entrer dans la boucle de jeu.
    nombre_utilisateur = -1
    tentative = 0
    
    while nombre_utilisateur != nombre_secret:
        nombre_utilisateur = int(input('Saisir un nombre : '))
        tentative  += 1
        message = ""
        
        # On vérifie si la proposition du joueur est
        # plus grande ou plus petite que le nombre secret
        if nombre_utilisateur > nombre_secret:
            message = "Plus petit"
        elif nombre_utilisateur < nombre_secret:
            message = "Plus grand"
            
        # S'il y a un début de message, c'est que l'utilisateur
        # n'a pas trouvé le nombre secret. Dans ce cas, on vérifie
        # sa distance par rapport au nombre secret
        if message:
            distance = abs(nombre_utilisateur - nombre_secret)
            if distance <= 2:
                message += ", tu brûles !"
            elif distance <= 10:
                message += ", tu chauffes !"
            print(message)
            
    print("Bravo, tu as trouvé en", tentative, "tentative(s)")
    ```
