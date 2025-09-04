# Les données en table

Les exemples donnés ci-après le seront sur la base d'une collection dont les objets sont les médailles remportées
par les pays ayant participés aux jeux olympiques de Beijing de 2022.
Voici un extrait du fichier `jo_beijing_2022.csv` contenant ces informations :

```csv
pays,or,argent,bronze
NORVÈGE,16,8,13
ALLEMAGNE,12,10,4
CHINE,9,4,2
```

[:material-download: `jo_beijing_2022.csv`](assets/jo_beijing_2022.csv){:download="jo_beijing_2022.csv"}


## Lecture du format CSV

Il existe deux modes de lecture de données CSV :

- Le mode **dictionnaire** : chaque ligne du fichier CSV est lue sous forme d'un dictionnaire
- Le mode **tableau** : chaque ligne du fichier CSV est lue sous forme d'un tableau

!!! example "Lecture d'un fichier CSV"

    === "Mode dictionnaire"
        ```python
        import csv
    
        fichier = open('jo_beijing_2022.csv') # (1)!
        lecteur_csv = csv.DictReader(fichier) # (2)!
        
        for ligne in lecteur_csv: 
            print(ligne) # (3)! 
    
        fichier.close() # (4)!
        ```
    
        1. Ouverture du fichier `jo_beijing_2022.csv`
        2. Création d'un lecteur de fichier CSV
        3. Parcours de chaque ligne du fichier CSV. L'affichage dans la console sera :
           ```
           {'pays':'NORVÈGE', 'or':16', 'argent':'8', 'bronze':'13'}
           {'pays':'ALLEMAGNE', 'or':'12', 'argent':'10', 'bronze':'4'}
           ...
           ```
        4. Fermeture du fichier `jo_beijing_2022.csv`

        Il est possible d'affecter à une variable l'ensemble des lignes en une seule intruction via la fonction `list()` :

        ```python
        import csv                      
    
        fichier = open('jo_beijing_2022.csv')
        medailles = list(csv.DictReader(fichier)) # (1)!
        fichier.close()
        ```
    
        1. Lecture des données du fichier sous forme d'un **tableau de dictionnaires**. La structure de la variable `table` sera :
           ```python
           [
              {'pays':'NORVÈGE', 'or':'16', 'argent':'8', 'bronze':'13'},
              {'pays':'ALLEMAGNE', 'or':'12', 'argent':'10', 'bronze':'4']},
              ...
           ]
           ```

    === "Mode tableau"

        ```python
        import csv
    
        fichier = open("jo_beijing_2022.csv") # (1)!
        lecteur_csv = csv.reader(fichier) # (2)!
        
        for ligne in lecteur_csv: 
            print(ligne) # (3)! 
    
        fichier.close() # (4)!
        ```
    
        1. Ouverture du fichier `jo_beijing_2022.csv`
        2. Création d'un lecteur de fichier CSV dont le caractère `,` est utilisé pour séparer les champs
        3. Parcours de chaque ligne du fichier CSV. L'affichage dans la console sera :
           ```
           ['pays','or','argent','bronze']
           ['NORVÈGE', '16', '8', '13']
           ['ALLEMAGNE', '12', '10', '4']
           ...
           ```
        4. Fermeture du fichier `jo_beijing_2022.csv`
    
        Il est possible d'affecter à une variable l'ensemble des lignes en une seule intruction via la fonction `list()` :
    
        ```python
        import csv
    
        fichier = open("jo_beijing_2022.csv")
        medailles = list(csv.reader(fichier)) # (1)!
        fichier.close()
        ```

        1. Lecture des données du fichier sous forme d'un **tableau doublement indexé**. La structure de la variable `table` sera :
           ```python
           [
              ['pays','or','argent','bronze']
              ['NORVÈGE', '16', '8', '13'],
              ['ALLEMAGNE', '12', '10', '4'],
              ...
           ]
           ```

## Parcours des données

En parcourant les données, il vous sera possible d'accéder aux données de chaque ligne et de mettre en oeuvre les
traitements de votre choix (affichage, recherche d'une valeur, calculs, ...)
Pour illustrer le parcours de données, affichons la liste des pays ayant obtenu au moins une médaille d'or.


!!! example "Parcours des données"

    === "Mode dictionnaire"

        ```python
        for i in range(len(medailles)):
            if int(medailles[i]['or']) > 0: # (1)!
                print(medailles[i]['pays'])
        ```
        
        1. Il y a ici une conversion vers entier à l'aide de la fonction `int()` car car toutes les données du fichier
           CSV sont interprété comme des chaînes de caractère au moment de la lecture par `csv.DictReader()`.


    === "Mode tableau"

        ```python
        for i in range(1, len(medailles)): # (1)!
            if int(medailles[i][1]) > 0: # (2)!
                print(medailles[i][0])
        ```

        1. Le parcours du tableau s'effecture depuis l'indice 1 pour ignorer la ligne d'en-têtes.
        2. Il y a ici une conversion vers entier à l'aide de la fonction `int()` car car toutes les données du fichier
           CSV sont interprété comme des chaînes de caractère au moment de la lecture par `csv.reader()`.


## Filtrage des données

Vous pourriez avoir besoin d'affiner les données en supprimant des lignes ou des colonnes superflues.
Pour illustrer le filtrage des données, nous allons créer une nouvelle liste ne contenant que les pays ayant obtenu au
moins une médaille d'or.

!!! example "Filtrage des lignes"

    === "Mode dictionnaire"

        ```python
        medailles_or = []
        
        for i in range(len(medailles)):
            if int(medailles[i]['or']) > 0:
                medailles_or.append(medailles[i])
        ```

    === "Mode tableau"
    
        ```python
        medailles_or = []
        
        for i in range(1, len(medailles)):
            if int(medailles[i][1]) > 0:
                medailles_or.append(medailles[i])
        ```

Nous souhaitons ne conserver que les colonnes du nom du pays et du nombre de médailles d'or.

!!! example "Sélection des colonnes"

    === "Mode dictionnaire"

        ```python
        pays = []
        
        for i in range(len(medailles_or)):
            pays.append({'pays': medailles_or[i]['pays'], 'or': medailles_or[i]['or']})
        ```

    === "Mode tableau"
    
        ```python
        pays = []
        
        for i in range(len(medailles_or)):
            pays.append([medailles_or[i][0], medailles_or[i][1]])
        ```


## Tri des données

Vous pourriez avoir besoin de trier les données en fonction d'une colonne et vouloir choisir si ce tri est croissant ou décroissant.
Pour illustrer le tri des données, nous allons trier le tableau des données filtrées dans l'ordre décroissant des médailles d'or.

!!! example "Tri des données"

    === "Mode dictionnaire"

        ```python
        def trier_par_medaille(ligne):
            return int(ligne['or'])
        
        pays.sort(key=trier_par_medaille, reverse=True)
        ```

    === "Mode tableau"
    
        ```python
        def trier_par_medaille(ligne):
            return int(ligne[1])
        
        pays.sort(key=trier_par_medaille, reverse=True)
        ```

## Écriture au format CSV

Nous souhaitons maintenant enregistrer le résultat de nos traitements dans un nouveau fichier CSV.

!!! example "Écriture au format CSV"

    === "Mode dictionnaire"
    
        ```python
        fichier = open('medailles_or.csv', 'w')
        
        w = csv.DictWriter(fichier, fieldnames=['pays', 'or'])
        w.writeheader()
        w.writerows(pays)
        
        fichier.close()
        ```
    
        Téléchargement du code complet : [:material-download: mode_dictionnaire.py](assets/mode_dictionnaire.py){:download="mode_dictionnaire.py"}

    === "Mode tableau"
    
        ```python
        fichier = open('medailles_or.csv', 'w')
        
        w = csv.writer(fichier)
        w.writerow(['pays', 'or'])
        w.writerows(pays)
        
        fichier.close()
        ```
        
        Téléchargement du code complet : [:material-download: mode_tableau.py](assets/mode_tableau.py){:download="mode_tableau.py"}


