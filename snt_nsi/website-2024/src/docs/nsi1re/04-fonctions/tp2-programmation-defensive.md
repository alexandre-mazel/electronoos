---
title: Programmation défensive
description: Introduction à la programmation défensive
---

# Programmation défensive

## Introduction

La programmation est une activité sujette aux erreurs.
Pour y remédier, il est nécessaire de tester régulièrement son code.
Ces précautions peuvent cependant rapidement devenir fastidieuses.
Il existe heureusement des techniques permettant d'automatiser ces tests et ainsi rendre les programmes plus fiables.

!!! target "Objectifs"

    - Savoir utiliser le module `doctest` afin de définir et lancer des tests ([:material-book-open-variant: Définir des fonctions](https://docs.python.org/fr/3.11/library/doctest.html){:target="_blank"})
    - Savoir utiliser des assertions afin de protéger l'utilisation d'une fonction

## Préparation

Vous allez créer des dossiers afin de ne pas mélanger vos productions numériques entre vos différentes matières et
travaux pratiques.

!!! note "Organisation de l'espace travail"

    === ":material-laptop: Ordinateur portable"

        1. Lancez l'application <i class="icon file-explorer"></i> **Explorateur de fichiers** 
           <span class="keys shortcut"><kbd>:fontawesome-brands-windows:</kbd><span>+</span><kbd>E</kbd></span>
        2. Accédez à votre dossier <i class="icon onedrive"></i> **OneDrive**
        3. Dans le dossier `OneDrive`, s'il n'y a pas de dossier `NSI`, créez-le
        4. Dans le dossier `NSI`, s'il n'y a pas de dossier `chapitre_04`, créez-le
        5. Dans le dossier `chapitre_04` créez le dossier `tp2`

    === ":material-desktop-tower: Ordinateur fixe"

        1. Depuis le bureau, double-cliquez sur l'icône intitulée **Zone personnelle**
        2. Dans la **zone personnelle**, s'il n'y a pas de dossier `NSI`, créez-le
        3. Dans le dossier `NSI`, s'il n'y a pas de dossier `chapitre_04`, créez-le
        4. Dans le dossier `chapitre_04` créez le dossier `tp2`

## Automatisation des tests

Il existe de plusieurs techniques d'automatisation des tests. Vous apprendrez à utiliser le module
[:material-book-open-variant: doctest](https://docs.python.org/fr/3.11/library/doctest.html)
qui permet d'écrire des jeux de tests directement dans une
[:material-book-open-variant: docstring](https://docs.python.org/fr/3.11/tutorial/controlflow.html#tut-docstrings).

Pour expérimenter ce module, vous devrez écrire la fonction `salutation` qui prend en paramètre le code d'une langue au
format [:material-link: ISO 639-1](https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1)
*(code pays représenté sur deux caractères)* et qui renvoie la formule de salutation correspondant à celui-ci.

Vous ne prendrez en compte que les langues listées dans le tableau ci-après.
Si le code de la langue n'est pas reconnu, le formule anglaise sera renvoyée par défaut.

<figure markdown>

| Code ISO 639-1      | Formule |
|---------------------|---------|
| `en` *(par défaut)* | *Hello* |
| `fr`                | *Salut* |
| `es`                | *Hola*  |

</figure>

### Préparation

!!! note "Instructions"

    1. Lancez l'application Thonny
    2. Créez un nouveau fichier `CTRL+N`
    3. Copiez/collez le code Python suivant :
        ```python
        def salutation(langue):
            """
            Renvoie le formule de salutation propre une langue donnée.
        
            langue -- Chaîne au format ISO 639-1
            """
        ```
    4. Enregistrez votre programme dans le fichier  `NSI\chapitre_04\tp2\salutation.py`

### Implémentation initiale

Vous allez maintenant implémenter la fonction `salutation` en ne prenant en compte que les langues `fr` et `es`
pour le moment. Il est donc question d'une fonction qui renvoie `'Salut'` si appelée avec l'argument `fr` 
et `'Hola'` si appelée avec l'argument `es`. 

L'anglais et la valeur par défaut seront pris en charge **dans un second temps**.

Vous testerez cette fonction **uniquement depuis la console Python**.
Le fichier `salutation.py` ne contiendra donc que la définition de la fonction `salutation` et rien d'autre.

!!! note "Instructions"

    1. Implémenter la fonction `salutation` pour `fr`et `es`
    2. Enregistrez vos modifications
    3. Lancez le programme afin que la fonction `salutation` soit disponible dans la console Python
    4. Testez manuellement la fonction `salutation` pour les langues `fr` et `es` depuis la console Python

??? success "Résultat attendu"

    Voici ce que vous devriez obtenir dans la console Python après y avoir manuellement appelé la fonction :
    
    === ":material-console: Console"

        ```
        >>> salutation("fr")
        'Salut'
        >>> salutation("es")
        'Hola'
        ```

??? tip "Conseil - Les raccourcis clavier de Thonny"

    Pour plus d'efficacité, notamment en l'absence de souris, faites usage des raccourcis clavier proposés par Thonny.
    Vous trouvez ci-dessous les plus utiles dans le cadre cet exercice.

    - Enregistrer le script courant <span class="shortcut">++ctrl+s++</span>
    - Exécuter le script courant <span class="shortcut">++f5++</span> 
    - Placer le curseur dans l'éditeur <span class="shortcut">++alt+e++</span> 
    - Placer le curseur dans la console <span class="shortcut">++alt+s++</span>
    - Récupérer les précédentes commandes saisies <span class="shortcut">++up++</span>

### Implémentation des tests

Vous allez maintenant modifier le fichier `salutation.py` afin d'ajouter un **jeu de tests** automatisés.
Observez ci-dessous une nouvelle version de la *docstring* de la fonction `salutation`. Vous constaterez que l'écriture
des tests
consiste simplement à recopier dans la *docstring* ce que vous pourriez obtenir en effectuant manuellement les tests 
depuis la console Python.

```python
def salutation(langue):
    """
    Renvoie le formule de salutation propre une langue donnée.
  
    langue -- Chaîne au format ISO 639-1
  
    >>> salutation('fr')
    'Salut'
    >>> salutation('es')
    'Hola'
    >>> salutation('en')
    'Hello'
    >>> salutation('??')
    'Hello'
    """
```

!!! note "Instructions"

    1. **Ajoutez** le jeu de tests à la *doctring* de la fonction `salutation`
    2. Ajoutez  le code ci-dessous d'import du module `doctest` et d'exécution des tests en fin de fichier :<br>
       *(Attention à l'indentation, ce code doit être en dehors du corps de la fonction `salutation`)*
        ```python
        if __name__ == "__main__":
            import doctest
            doctest.testmod()
        ```
    3. Exécutez le programme

??? success "Résultat attendu"

    Vous devriez obtenir l'affichage console ci-dessous.
    Vous constaterez que deux tests n'ont pas le résultat attendu. 
    Il s'agit de l'anglais et la langue par défaut qui n'ont pas encore été implémentés.

    === ":material-console: Console"

        ```text
        **********************************************************************
        File "exercice1.py", line 12, in __main__.salutation
        Failed example:
        salutation('en')
        Expected:
        'Hello'
        Got nothing
        **********************************************************************
        File "exercice1.py", line 14, in __main__.salutation
        Failed example:
        salutation('??')
        Expected:
        'Hello'
        Got nothing
        **********************************************************************
        1 items had failures:
        2 of   4 in __main__.salutation
        ***Test Failed*** 2 failures.
        ```

### Implémentation finale

Terminez d'écrire le code de la fonction `salutation` en prenant en charge la langue anglaise, sans oublier de
l'utiliser comme langue par défaut.
Si votre implémentation est correcte, l'exécution de votre programme ne devrait plus entrainer l'affichage de tests en
erreur dans la console.

### Application

Vous allez maintenant appliquer les concepts découverts dans le cadre de l'exercice précédent.
Pour cela, vous devrez implémenter une nouvelle fonction, en écrire la documentation et les tests.

!!! note "Consigne"

    Écrire la fonction `initiales` ayant pour paramètres `prenom` et un `nom` et renvoyant les initiales en majuscule.
    On ne prendra en compte que la première lettre du prénom et du nom même s'il s'agit d'un prénom composé ou de 
    plusieurs noms. Voici un exemple d'appel de la fonction depuis la console Python :

    ```text
    >>> initiales("grace", "Hopper")
    'GH'
    ```

    1. Créer un nouveau programme et l'enregistrer dans `NSI\chapitre_04\tp2\initiales.py`
    2. Implémenter la fonction `initiales`
    3. Écrire la documentation *docstring*
    4. Écrire des tests pertinents au format *doctest*
    4. Ajouter le code d'exécution du jeu de tests
    5. Enregistrer le programme
    6. Vérifiez que les tests fonctionnent

??? tip "Aide - Récupérer le premier caractère d'une chaîne"

    Vous pouvez obtenir le caractère en position *n* d'une variable `message` en utilisant l'expression 
    `#!python message[n]`. L'expression pour récupérer le premier caractère de `#!python message` serait 
    `#!python message[0]` car la numérotation se fait à partir de zéro.

    === ":material-console: Console"

        ```
        >>> message = 'Bonjour'
        >>> message[0]
        'B'
        ```

??? tip "Aide - Convertir une chaîne en majuscules"

    Vous pouvez obtenir la conversion en majuscules d'une variable `message` en utilisant l'expression `message.upper()`

    === ":material-console: Console"

        ```
        >>> message = 'Bonjour'
        >>> message.upper()
        'BONJOUR'
        ```

## Protection des fonctions

Vous allez implémenter une fonction dont l'algorithme n'est correct que dans certaines conditions.
Pour empêcher toute mauvaise utilisation de cette fonction, vous allez devoir la protéger.

### Préparation

Soit la fonction `multiplication` ayant pour paramètres `x` et `y` deux entiers positifs ou nuls.
Cette fonction renvoie le produit de `x` par `y` sans utilisation de l'opérateur `*` selon l'algorithme décrit dans la
*docstring*

```python
def multiplication(x, y):
    """
    Renvoie la produit de x par y.
  
    x -- Entier positif non nul
    y -- Entier positif non nul
  
    Algorithme :
       total ← 0
       Répéter y fois :
          total ← total + x
       renvoyer total
    """
```

!!! note "Instructions"
    
    1. Lancez l'application Thonny
    2. Créez un nouveau fichier `CTRL+N`
    3. Copiez/collez le code Python de la fonction `multiplication`
    4. Implémentez l'algorithme
    5. Enregistrez votre programme dans le fichier `NSI\chapitre_04\tp2\multiplication.py`
    6. Lancez le programme afin que la fonction `multiplication` soit disponible dans la console Python
    7. Vérifiez que vous obtenez `4` pour l'appel de fonction `multiplication(2, 2)`

### Cas particuliers

!!! note "Instructions"

    Testez les appels de fonction ci-dessous depuis la console Python :

    - `#!python multiplication(2, -2)`
    - `#!python multiplication(-2, 2)`
    - `#!python multiplication(1.1, 2)`
    - `#!python multiplication(2, 1.1)`

??? success "Résultat attendu"

    Vous devriez obtenir l'affichage console ci-dessous.

    === ":material-console: Console"

        ```text
        >>> multiplication(2, -2)
        0
        >>> multiplication(-2, 2)
        -4
        >>> multiplication(1.1, 2)
        2.2
        >>> multiplication(2, 1.1)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "multiplication.py", line 15, in multiplication
            for _ in range(y):
        TypeError: 'float' object cannot be interpreted as an integer
        ```

Vous constaterez des résultats erronés, voire des erreurs, selon les arguments d'appel.
En effet, l'algorithme est conçu pour ne fonctionner qu'avec des entiers positifs ou nuls.
Il faudrait donc protéger la fonction `multiplication` de tout usage non conforme et ainsi éviter l'introduction 
d'anomalies au sein de programmes plus vastes.

Pour cela, vous allez utiliser des **assertions**.
Une assertion est une condition qui doit être vraie pour poursuivre l'exécution d'un programme.
L'exécution de la fonction `multiplication` ne doit être possible que si les **préconditions** suivantes sont 
respectées :

- `x` est un entier
- `x` est supérieur ou égal à 0
- `y` est un entier
- `y` est supérieur ou égal à 0

En Python, l'instruction `assert` permet la définition d'une assertion.
Voici l'équivalent en assertions Python des préconditions listées pour la fonction `multiplication` :

```python
assert isinstance(x, int)  # valide si x est de type int
assert x >= 0              # valide si x est positif ou nul
assert isinstance(y, int)  # valide si y est de type int
assert y >= 0              # valide si y est positif ou nul
```

### Implémentation des assertions

Vous allez ajouter les assertions à la fonction `multiplication`.
Celles-ci doivent être les premières instructions de la fonction et sont à placer juste après la *docstring*.
Une fois les assertions en place, toute précondition non respectée déclenchera une `AssertionError`.

```python
def multiplication(x, y):
    """
    --- Docstring ---
    """
    assert isinstance(x, int)
    assert x >= 0
    assert isinstance(y, int)
    assert y >= 0

    # --- Code ---
```

!!! note "Instructions"

    1. Implémenter les assertions
    2. Enregistrez vos modifications
    3. Lancez le programme afin que la fonction `multiplication` soit à jour dans la console Python
    4. Testez de nouveau les appels suivant dans la console Python :
        - `#!python multiplication(2, -2)`
        - `#!python multiplication(-2, 2)`
        - `#!python multiplication(1.1, 2)`
        - `#!python multiplication(2, 1.1)`

??? success "Résultat attendu"

    Vous devriez obtenir l'affichage console ci-dessous. Les lignes importantes sont surlignées.

    === ":material-console: Console"

        ```text hl_lines="1 5"
        >>> multiplication(2, -2)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "multiplication.py", line 17, in multiplication
            assert y >= 0
        AssertionError
        ```

        ```text hl_lines="1 5"
        >>> multiplication(-2, 2)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "multiplication.py", line 15, in multiplication
            assert x >= 0
        AssertionError
        ```
        
        ```text hl_lines="1 5"
        >>> multiplication(1.1, 2)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "multiplication.py", line 14, in multiplication
            assert isinstance(x, int)
        AssertionError
        ```

        ```text hl_lines="1 5"
        >>> multiplication(2, 1.1)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "multiplication.py", line 16, in multiplication
            assert isinstance(y, int)
        AssertionError
        ```

### Application

Vous allez maintenant appliquer les concepts introduits dans le cadre des exercices précédents.
Pour cela, vous devrez implémenter une nouvelle fonction, en écrire la documentation, les tests et les préconditions.


Selon le même principe que l'exercice 3, écrire la fonction `puissance` ayant pour paramètres `x` et `y` deux entiers
positifs ou nuls.
Cette fonction renvoie la valeur de `x` élevé à la puissance `y`. Utiliser uniquement l'opérateur `*` et une boucle.

- Enregistrer le code dans un fichier fichier `puissance.py`
- Écrire la documentation docstring (description de la fonction et des paramètres)
- Écrire l'algorithme dans la doctring
- Écrire les tests que vous jugerez pertinents au format doctest
- Écrire les assertions


!!! note "Consigne"

    Écrire la fonction `puissance` ayant pour paramètres `n` et `p` deux entiers positifs ou nuls.
    Cette fonction renvoie la valeur de `n` élevé à la puissance `p` sans utiliser l'opérateur `**`.

    ```text
    >>> puissante(2, 3)
    8
    >>> puissante(2, 0)
    1
    ```

    1. Définir la fonction `puissance`
    2. Écrire la documentation *docstring*
    3. Écrire l'algorithme dans la *docstring*
    3. Écrire des tests pertinents au format *doctest*
    4. Ajouter le code d'exécution du jeu de tests
    5. Implémenter la fonction sans oublier les assertions
    6. Enregistrer le programme dans le fichier `NSI\chapitre_04\tp2\puissance.py`
    7. Vérifiez que les tests et les assertions fonctionnent