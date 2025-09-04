---
title: Chapitre 3 - Bases de la programmation - TP1 Python en mode interactif
description: Découverte du langage Python à travers son mode interactif
---

# Python en mode interactif

## Introduction

Python est un langage interprété.
Il est donc nécessaire de disposer d'un interpréteur Python pour exécuter un programme écrit dans ce langage.

!!! info "Les interpréteurs Python"

    Vous avez la possibilité de trouver un interpréteur :

    - sur votre calculatrice graphique [TI-83 Premium CE Edition Python](https://education.ti.com/fr/produits/calculatrices/graphiques/ti-83-premium-ce-edition-python){:target="_blank"} ou [Numworks](https://www.numworks.com/fr/calculatrice/python/){:target="_blank"} ;
    - en ligne avec [Baston](https://console.basthon.fr/){:target="_blank"} ;
    - en installant les logiciels éducatifs [Thonny](https://thonny.org/){:target="_blank"} ou [EduPython](https://edupython.tuxfamily.org/){:target="_blank"} ;
    - en installant l'[interpréteur Python officiel](https://www.python.org/downloads/){:target="_blank"} ;
    - en utilisant l'interpréteur préinstallé sur macOS et certaines distributions Linux.

Ces travaux pratiques ont pour objectif la découverte du langage Python à travers son mode interactif.

## Préparation

### Lancement de Linux

Vous utiliserez l'interpréteur Python préinstallé d'un système d'exploitation Linux.
Pour cela, vous allez relancer l'émulateur Linux en ligne découvert dans le cadre des travaux pratiques sur l'
interpréteur de commande.

!!! note "Lancement d'un CLI Linux en ligne"

    1. Lancez un navigateur Web
    2. Connectez-vous à l'adresse [https://bellard.org/jslinux](https://bellard.org/jslinux){:target="_blank"}
    3. Identifiez la version **x86 Alpine Linux 3.12.0 Console**
    4. Cliquez sur **click here** pour lancer l'émulation

### Lancement de Python

Le langage Python est généralement installé par défaut sur les systèmes d'exploitation Linux et macOS.
Il est disponible depuis l'interpréteur de commande sous forme d'un ou plusieurs executables.

!!! note "Identification de l'interpréteur Python"

    1. Retournez à l'interpréteur de commande Linux
    2. Saisissez le texte `py` et appuyer deux fois sur la touche ++tab++ de votre clavier.

!!! success "Résultat"

    L'interpréteur vous affiche toutes les commandes disponibles dont le nom commence par `py` :

    ```
    localhost:~# py
    pydoc             pygmentex         python2.7         python3.8
    pydoc3            python            python3           python3.8-config
    pydoc3.8          python2           python3-config    pythontex
    ```

Il existe plusieurs versions du langage Python.
Vous allez appeler les commandes `python` avec l'option l'option `--version`.
Vous pourrez ainsi verifier la version du langage prise en charge par chacune d'elles.

!!! note "Version du langage"

    1. Retournez à l'interpréteur de commande Linux
    2. Saisissez `python --version` et appuyez sur ++enter++
    3. Saisissez `python3 --version` et appuyez sur ++enter++

!!! success "Résultat"

    L'interpréteur vous affiche la version du langage prise en charge par les exécutables `python` et `python3` :

    ```
    localhost:~# python --version
    Python 2.7.18
    localhost:~# python3 --version
    Python 3.8.3
    ```

Python 2 [n'est plus supporté](https://www.python.org/doc/sunset-python-2/){:target="_blank"}
Vous devez donc veiller à toujours utiliser la version 3.
Nous en sommes aujourd'hui à la version 3.11, mais la version 3.8 reste amplement suffisante dans le cadre de
l'apprentissage de la programmation en NSI.

!!! note "Lancement du programme `python3`"

    1. Retournez à l'interpréteur de commande Linux
    2. Saisissez `python3` et appuyez sur ++enter++
    3. Patientez le temps du démarrage de l'application jusqu'à l'apparition de l'affichage suivant :

    ```text
    localhost:~# python3
    Python 3.8.3 (default, May 15 2020, 01:53:50)
    [GCC 9.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    ```

Vous êtes maintenant dans le mode interactif de Python.
Dans ce mode, chaque commande saisie sera immédiatement traitée par l'interpréteur Python qui, selon la saisie,
présentera ou non un résultat.

!!! warning "Important"

    Toutes les commandes saisies dans le cadre de ces travaux pratiques devront se faire en **mode interactif** Python.

## Les nombres

### Premières saisies

Vous êtes en train d'utiliser Python en mode interactif aussi appelé **console**.
Dans ce mode, Python évalue immédiatement toute expression ou instruction que vous lui soumettez.

!!!note "Expressions simples"

    1. Saisissez le littéral `10` et appuyez sur ++enter++
    2. Qu'observez-vous ?
    3. Saisissez l'expression `10 + 10` et appuyez sur ++enter++
    4. Qu'observez-vous ?

!!! success "Résultat"

    ```
    >>> 10
    10
    >>> 10 + 10
    20
    >>>
    ```
    
    Lorsqu'une commande correspond à une **expression**, l'interpréteur Python l'évalue et affiche sa valeur.
    Il attend ensuite une nouvelle commande de la part de l'utilisateur.

### Opérations mathématiques

Traduisez chacune des propositions suivantes en une expression Python à soumettre à l'interpréteur interactif.

!!!abstract "Opérations sur les nombres"

    - Une addition
    - Une soustraction
    - Une multiplication
    - Une division
    - Une division euclidienne (aussi appeléee *division entière*)
    - Un reste de division euclidienne (aussi appelé *modulo*)
    - Une opération contenant à la fois un entier et un flottant

### Recherche d'expressions

À l'aide de l'interpréteur Python **uniquement**, trouver la réponse aux questions suivantes :

!!!question "Questions"

    - Quelle est la valeur décimale du nombre hexadécimal `7E6` ? *(voir activité 1 - exercice 1)*
    - Quelle est la valeur décimale du nombre binaire `11111100111` ? *(voir activité 1 - exercice 1)*
    - Le nombre `2479939` appartient-il à la table de 7 ?
    - Le nombre `4328361193` est-il divisible par 77 ?
    - Quelle est la valeur de 2 puissance 16 ?
    - La taille des nombres que vous pouvez utiliser est-elle limitée ?

### Compréhension d'expressions

Python dispose de [fonctions mathématiques](https://docs.python.org/fr/3/library/math.html) accessibles en important le
module `math`.

!!!note "Import du module `maths`"

    1. Retournez à la console Python
    2. Saisissez `import math` et appuyez sur ++enter++
    3. Testez l'expression `math.pi`

    ```
    >>> import math
    >>> math.pi
    3.141592653589793
    >>>
    ```

Après avoir importé le module `math`, testez les expressions suivantes et expliquez-les à partir du résultat obtenu et
d'expérimentations avec d'autres valeurs.

!!!abstract "Expressions inconnues"

    - `#!python math.sqrt(100)`
    - `#!python math.ceil(19.6)`
    - `#!python math.floor(19.6)`
    - `#!python math.fabs(-10)`
    - `#!python math.sin(math.radians(90))`

## Les chaînes de caractères

### Recherche d'expressions

Traduisez chacune des propositions suivantes en une expression Python à soumettre à l'interpréteur interactif.

!!!abstract "Opérations sur les nombres"

    - Une chaîne de caractères en utilisant le délimiteur `"`
    - Une chaîne de caractères en utilisant le délimiteur `'`
    - Une chaîne de caractères en utilisant le délimiteur de votre choix et contient à la fois le caractère `'` et le caractère `"`
    - Une **concaténation** de deux chaînes de caractères
    - Une **répétition** d'une chaîne de caractères
    - Un test d'**appartenance** d'une chaîne à une autre chaîne
    - Un test de **non appartenance** d'une chaîne à une autre chaîne

### Compréhension d'expressions

Testez les expressions suivantes et expliquez-les à partir du résultat obtenu et d'expérimentations avec d'autres
valeurs.

!!!abstract "Expressions inconnues"

    - `#!python len('Hello')`
    - `#!python 'Bonjour tout le monde'[:7]`
    - `#!python 'Bonjour tout le monde'[16:]`
    - `#!python 'Bonjour tout le monde'[8:12]`
    - `#!python 'majuscules'.upper()`
    - `#!python 'MINUSCULES'.lower()`
    - `#!python 'Bonjour tout le monde'.replace("Bonjour", "Au revoir")`

## Les variables

### Affectation

L'opération permettant de donner une valeur à une variable s'appelle une **affectation**.
L'opérateur d'affectation est `=`. Il a pour opérande gauche un **nom de variable** et pour opérande droit, une **expression**.

!!!note "Première affectation"

    1. Retournez à la console Python
    2. Saisissez l'instruction `#!python x = 2 + 2` et appuyez sur ++enter++
    3. Vous devez obtenir le résultat suivant :
    
    ```
    >>> x = 2 + 2
    >>> 
    ```

!!!question "Question"

    Lorsque nous soumettions une expression à l'interpréteur Python, celui-ci nous présentait systématiquement la valeur de son évaluation.
    Mais pour l'affectation, Python n'affiche rien. Pourquoi selon vous ?

    ```
    >>> 2 + 2
    >>> 4
    >>> x = 2 + 2
    >>>
    ```

### Accès à la valeur d'une variable

Pour accéder à la valeur d'une variable, il suffit d'utiliser une expression contenant le nom de la variable.

!!!note "Première affectation"

    1. Retournez à la console Python
    2. Saisissez l'expression `#!python x` et appuyez sur ++enter++
    3. Vous devez obtenir le résultat suivant :

    ```
    >>> x
    4
    >>> 
    ```

!!!question "Question"

    Selon vous, pourquoi l'interpréteur Python affiche-t-il cette-fois une valeur ?

### Évaluer la valeur des variables

Examinez chaque série d'instructions et essayez de prédire leur résultat. Confirmez-les à l'aide de l'interpréteur.

???example "Cas de l'affectation d'une expression"

    ```
    >>> x = "Ha " * 3 + "!"
    >>> x
    ?
    ```

???example "Cas de la réutilisation d'une même variable"

    ```
    >>> x = 2
    >>> x = (x * 2) ** x
    ?
    ```

???example "Cas de l'utilisation de deux variables"

    ```
    >>> x = 1
    >>> x
    1
    >>> y = 2
    >>> x = x + y
    >>> y = x ** y
    >>> x
    ?
    >>> y
    ?
    ```

???example "Cas d'une opération classique en programmation"

    ```
    >>> x = 5
    >>> y = 9
    >>> x
    5
    >>> y
    9
    >>> tmp = x
    >>> x = y
    >>> y = tmp
    >>> x
    ?
    >>> y
    ?
    ```

    !!!question "Question"
      
        Que cherchons-nous finalement à faire avec ces trois lignes de code ?
    
        ```python
        tmp = x
        x = y
        y = tmp
        ```

## Les anomalies

En programmation, c'est **inévitable**, vous devrez faire face à de très nombreuses anomalies.
N'y voyez surtout pas un échec, voyez y plutôt un jeu, une énigme à résoudre, une enquête à mener.
Prenez le temps de bien lire les messages d'erreur et d'essayer de les comprendre.

!!!warning "Attention"

    Avant de commencer, vous devez partir d'un environnement interactif **vierge** :

    1. Quittez le mode interactif à l'aide de l'instruction `quit()`
    2. Relancez le mode interactif à l'aide de la commande `python3`

Toutes les commandes ci-après provoquent une anomalie ou un comportement inattendu. À vous de trouver une explication.

!!!abstract "Menez l'enquête !"

    - `#!python 10 / 0`
    - `#!python n = n + 1`
    - `#!python false`
    - `#!python '3' + 3`
    - `#!python 'A' < 65`
    - `#!python math.sqrt(4)`
    - `#!python 2,5`
    - `#!python import math` <br> `math.cos(math.radians(90))` <br> *(on rappelle que le cosinus de 90 degrés vaut 0)*
    - `#!python 0.1 + 0.2 == 0.3`

## Conclusion

Une fois que vous avez terminé ces travaux pratiques, **appelez votre enseignant** afin qu'il puisse répondre à vos interrogations.
Vous pourrez ensuite vous exercer au langage Python en lançant l'activité bonus, **uniquement avec l'accord de votre enseignant**.

??? tip "Bonus"

    Exercez-vous à la programmation Python de façon ludique avec [Pyrates](https://py-rates.fr/){:target="_blank"}.
