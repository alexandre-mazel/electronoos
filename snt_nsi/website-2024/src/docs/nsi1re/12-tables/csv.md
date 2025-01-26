# Fichiers CSV : Traitement des données en tables

## Données en tables

Une des utilisations principales de l’informatique de nos jours est le **traitement de quantités importantes de données** dans des domaines très variés :

* un site de commerce en ligne peut avoir à gérer des bases données pour des dizaines de milliers d’articles en vente, de clients, de commandes ;
* un hôpital doit pouvoir accéder efficacement à tous les détails de traitements de ses patients ;
* un éditeur de jeux vidéo doit pouvoir stocker les informations relatives à chaque joueur et chaque élément du jeu ;
* etc …

De tels traitements requierent souvent des logiciels de **gestion de base de données (SGDB)**, qui sont des programmes hautement spécialisés pour effectuer ce genre de tâches le plus efficacement et sûrement possible. L'étude plus détaillée des SGBD est au programme de terminale. Il est cependant facile de mettre en œuvre les opérations de bases sur certaines structures dans un langage de programmation comme Python.

Il est en effet possible que de simples jeux de données soient **organisés en tables**. En informatique, une **table de données** correspond à une liste de **p-uplets nommés** qui partagent les mêmes **descripteurs**. 

!!! example "Exemple"
	Par exemple on peut considérer la table suivante :

	| Nom | Rang | Couleur du sabre |
	|:-----:|:------:|:-------------:|
	| Luke Skywalker | Apprenti/Maitre Jedi | Vert |
	| Anakin Skywalker |Apprenti Jedi | Bleu |
	| Yoda | Maitre Jedi | Vert |
	| Conte Dooku | Seigneur Sith | Ecarlate |
	| Darth Vader | Apprenti Sith | Ecarlate |
	| Rey | Apprentie Jedi | Jaune |

	Chacune des lignes, appelée aussi **enregistrement**, est un  **p-uplet nommé** de taille 3.
	Chaque enregistrement correspond donc à un **dictionnaire** en Python. La première ligne correspond à :


	```python
	{'Nom' : 'Luke Skywalker', 'Rang' :'Apprenti/Maitre Jedi', 'Couleur du sabre' : 'Vert'}
	```


## Fichiers CSV

Le format **CSV** (pour *Comma Separated Values*, soit en français *valeurs séparées par des virgules*) est un format très pratique pour représenter des données structurées.

Dans ce format, **chaque ligne représente un enregistrement** et, sur une même ligne, **les différents champs** de l’enregistrement sont **séparés par une virgule** (d’où le nom).

Pour des raisons pratiques, il est possible en fait de spécifier le caractère de séparation entre chaque champ, qui peut donc être `:`, `;`, `/`, etc...

Nous allons dans la suite de cette partie utiliser un fichier nommé `countries.csv`, téléchargeable [ici](assets/countries.csv){: target = "_blank"}.

!!! question "Exercice 1"
	
	Une fois le fichier téléchargé, vous pouvez l'ouvrir avec un éditeur de texte brut, comme `Notepad`, `Notepad ++` ou même `Thonny`.

	=== "Enoncé"
			
		1. Quel est le symbole utilisé pour séparer les champs dans le fichier  `countries.csv`?
		2. Combien de champs différents sont présents et quels sont leurs descripteurs ?
		3. Il est aussi possible d'utiliser un **tableur** comme `LibreOffice.Calc` pour lire un fichier CSV. Vous pourrez constater que `LibreOffice.Calc` vous demande un certain nombre d'informations sur le contenu du fichier avant de l'ouvrir réellement. Quels intérêt voyez-vous à l'utilisation d'un tableur ? Quelles en sont les limites ?		
		
	=== "Réponses"
		1. C'est le point-virgule
		2. Il y a 8 champs dont les descripteurs sont :
		
			* ISO
			* Name
			* Capital_Id
			* Area
			* Population
			* Continent
			* Currency_Code
			* Currency_Name


		3. Le tableur permet de visualiser rapidement les descripteurs et les données, quand elles ne sont pas trop nombreuses. Un tableur est limité a 1 000 000 de lignes, alors qu'un fichier CSV n'est pas limité (ce qui n'empêche pas des problèmes liées à la quantité de mémoire de l'ordinateur).

## Module CSV 

### Lecture de base

Un fichier `csv` étant un fichier texte, il est tout à fait possible de lire les données grâce aux méthodes classiques des fichiers(revoir votre cours sur les fichiers en Python<!-- [ici](Miscellanees\Bases_Python\Fichiers_Textes.md){: target="_blank"}-->) :

```python
>>> with open('countries.csv','r',encoding='utf8',newline='') as file:
		contenu = file.readlines()
		print(contenu)
```

Le résultat est peu lisible, et difficilement exploitable ainsi. Mais il est tout à fait possible de reconstituer correctement chaque enregistrement, 
en utilisant des méthodes de chaines de caractères (*on se limite aux 5 premiers enregistrements pour des raisons de lisbilités dans l'interpréteur*) :

```python
for line in contenu[:5] :
		print( line.replace('\n','') )
        
"""
ISO;Name;Capital_Id;Area;Population;Continent;Currency_Code;Currency_Name
AD;Andorra;3041563;468;84000;EU;EUR;Euro
AE;United Arab Emirates;292968;82880;4975593;AS;AED;Dirham
AF;Afghanistan;1138958;647500;29121286;AS;AFN;Afghani
AG;Antigua and Barbuda;3576022;443;86754;NA;XCD;Dollar
"""
```
On peut alors récupérer les **descripteurs** :

```python
print(contenu[0])
# ISO;Name;Capital_Id;Area;Population;Continent;Currency_Code;Currency_Name
```

Et le premier enregistrement :

```python
print(contenu[1])
# AD;Andorra;3041563;468;84000;EU;EUR;Euro
```

Cependant cette solution n'est pas des plus efficace, car **le lien entre descripteurs et valeurs n'est pas direct**.

### Lire un fichier CSV, premiers traitements

*Dans la suite du cours, il sera nécessaire d'adapter au fur et à mesure un fichier python !*

Le module `csv`  est un des modules présents dans toute installation Python. Comme tout module, il est disponible par import direct :

``` python 
import csv
```

Une fois importé, il offre de nombreuses possibilités, décrites dans [la doc Python](https://docs.python.org/fr/3.6/library/csv.html){: target="_blank"}, 
dont la méthode `reader` qui permet de récupérer les enregistrements un par un :

```python
import csv
import collections
def load_csv_to_namedtuple( nom_fichier: str, nom_type_objet: str, csv_delimiter:str = ';' ) -> list:
    """
    Charge un fichier csv et la convertit en namedtuple.
    Elle va cree un type de nammedtuple d'un type qui sera nomme nom_type_objet
    Return: Une liste d'enregistrement sous la forme d'une liste de nammedtuple.
    
    - nom_fichier: nom d'un fichier existant de type csv
    - nom_type_objet: nom du type d'enregistrement a creer
    - csv_delimiter: specifie un autre delimiteur de champs dans le csv
    """
    
    fichier = open( nom_fichier, "r" )
    reader = csv.reader( fichier, delimiter = csv_delimiter, skipinitialspace = True  )

    # creation du type de donnees
    noms_des_champs = next( reader )
    
    ClassType = collections.namedtuple( nom_type_objet, noms_des_champs )  # get names from column headers

    # lis et ajoute chaque enregistrement du fichier
    liste_objets = []
    for ligne in reader:
        
        # transforme les donnees contenant des " en chaines et les autres en int ou en float
        for i in range(len(ligne)):
            if ligne[i][0] == '"' and ligne[i][-1] == '"':
                ligne[i] = ligne[i][1:-1]
            
            if not ligne[i].isnumeric():
                pass
            else:
                if '.' in ligne[i]:
                    ligne[i] = float(ligne[i])
                else:
                    ligne[i] = int(ligne[i])
        # maintenant que toutes les donnees sont du bon type, on peut créer d'un appel un n-uplet nommé du bon type et l'ajouter à notre liste.
        liste_objets.append( ClassType( *ligne ) )  # l'etoile permet de "derouler la liste" (unroll), ainsi chaque element de la liste devient un parametre de la fonction
    
    fichier.close()
    
    return liste_objets
# load_csv_to_namedtuple - end

# utilisation de la fonction load_csv_to_namedtuple pour lire le fichier et creer un tableau des pays:
countries = load_csv_to_namedtuple( "countries.csv", "Country")

print( "Nbr Countries:", len(countries) )
# Nbr Countries: 243

```

La variable `countries` fait donc référence à une liste de n-uplet nommés, ayant tous les mêmes descripteurs. Une fois le programme exécuté, on peut donc tester dans le shell les commandes suivantes :


```python
print( countries[2] )

# Country(ISO='AD', Name='Andorra', Capital_Id=3041563, Area=468, Population=84000, Continent='EU', Currency_Code='EUR', Currency_Name='Euro')
```

On peut bien entendu connaître le nombre d'enregistrements contenus dans la variable `countries` :

```python
print( len(countries) )
# 243
```

On peut alors utiliser la liste `countries` pour faire des recherches, des calculs, des filtrages, des tris... 

Par exemple, nous pouvons chercher à obtenir la liste des pays dont la devise est l'euro:

```python
for c in countries:
    if c['Currency_Code'] == 'EUR':
       print(c.Name)
       
"""
Andorra
Austria
Aland Islands
Belgium
Saint Barthelemy
Cyprus
Germany
Estonia
Spain
Finland
France
French Guiana
Guadeloupe
Greece
Ireland
Italy
Kosovo
Lithuania
Luxembourg
Latvia
Monaco
Montenegro
Saint Martin
Martinique
Malta
Netherlands
Saint Pierre and Miquelon
Portugal
Reunion
Slovenia
Slovakia
San Marino
French Southern Territories
Vatican
Mayotte
"""
```




!!! question "Exercice"


	=== "Enoncé"
		1. Écrire une boucle permettant de lister les codes de toutes les monnaies qui s’appellent `‘Dollar’`.
		
		2. Écrire une boucle permettant de lister les pays du continent Nord-Américain, sous la forme `Nom, Superficie, Population`
		
	=== "Réponses"
	
		1. Le code :
		
			``` python
			for c in countries:
               if c.Currency_Name == 'Dollar':
                 print( c.Currency_Code )
            """
            XCD
            XCD
            USD
            AUD
            BBD
            BMD
            BND
            BSD
            BZD
            CAD
            AUD
            ...
            """
			```
			
		2. Le code :
			``` python
            for c in countries:
                if c.Continent == 'NA':
                    print( c.Name, ", superficie:", c.Area, ", population:", c.Population )
            """
            Antigua and Barbuda , superficie: 443 , population: 86754
            Anguilla , superficie: 102 , population: 13254
            Aruba , superficie: 193 , population: 71566
            Barbados , superficie: 431 , population: 285653
            Saint Barthelemy , superficie: 21 , population: 8450
            ...
            """
			```

### Les données numériques 

Nous avons de la chance, notre fonction `load_csv_to_namedtuple` a convertit les types qui ressemblaient à des entiers en valeurs de type entière.

Nous allons tester de les utiliser comme critère de selection.

!!! question "Exercice"
	=== "Enoncé"

		Écrire un parcours de liste affichant le nom, le continent et la superficie des pays de plus de 100 millions d'habitants

	=== "Réponse"
    
    ``` python
    for c in countries:
        if c.Population > 10**8:
            print( c.Name, ": continent:", c.Continent, ", superficie:", c.Area, ", population:", c.Population )
    """
    Bangladesh : continent: AS , superficie: 144000 , population: 156118464
    Brazil : continent: SA , superficie: 8511965 , population: 201103330
    China : continent: AS , superficie: 9596960 , population: 1330044000
    Indonesia : continent: AS , superficie: 1919440 , population: 242968342
    India : continent: AS , superficie: 3287590 , population: 1173108018
    ...
    """
    ```

### Trier les données

Les résultats precédents sont encore peu lisibles, il serait préférable que les données obtenues soient triées. On va utiliser la fonction *built-in* `sorted` :

```python
out = []
for c in countries:
    if c.Area < 300:
        out.append(c)
out_sorted = sorted(out)
for c in out_sorted:
    print(c)
"""
Country(ISO='AI', Name='Anguilla', Capital_Id=3573374, Area=102, Population=13254, Continent='NA', Currency_Code='XCD', Currency_Name='Dollar')
Country(ISO='AS', Name='American Samoa', Capital_Id=5881576, Area=199, Population=57881, Continent='OC', Currency_Code='USD', Currency_Name='Dollar')
Country(ISO='AW', Name='Aruba', Capital_Id=3577154, Area=193, Population=71566, Continent='NA', Currency_Code='AWG', Currency_Name='Guilder')
Country(ISO='BL', Name='Saint Barthelemy', Capital_Id=3579132, Area=21, Population=8450, Continent='NA', Currency_Code='EUR', Currency_Name='Euro')
Country(ISO='BM', Name='Bermuda', Capital_Id=3573197, Area=53, Population=65365, Continent='NA', Currency_Code='BMD', Currency_Name='Dollar')
...
"""
```

On obtient bien une liste triée, mais par ordre alphabétique, ce qui est peu pertinent. En effet, pour trier une table, il faut préciser selon quels **critères**.

On va donc passer un argument supplémentaire à la fonction `sorted` une **clé de tri**. 

Dans Python, la clé doit être **une fonction** permettant d'extraire la valeur à trier. 
On va donc créer une fonction qui va renvoyer la valeur voulue selon l'enregistrement passé en paramètre. 
Ici on va passer un **enregistrement** et on veut donc trier selon l'élément Area:

```python
def getArea(c):
    return c.Area
```

Puis on va passer cette fonction à la fonction `sorted` dans le paramêtre `key`:


```python
out_sorted = sorted(out, key = getArea)
for c in out_sorted:
    print(c)
"""
Country(ISO='VA', Name='Vatican', Capital_Id=6691831, Area=0.44, Population=921, Continent='EU', Currency_Code='EUR', Currency_Name='Euro')
Country(ISO='MC', Name='Monaco', Capital_Id=2993458, Area=1.95, Population=32965, Continent='EU', Currency_Code='EUR', Currency_Name='Euro')
Country(ISO='GI', Name='Gibraltar', Capital_Id=2411585, Area=6.5, Population=27884, Continent='EU', Currency_Code='GIP', Currency_Name='Pound')
Country(ISO='CC', Name='Cocos Islands', Capital_Id=7304591, Area=14, Population=628, Continent='AS', Currency_Code='AUD', Currency_Name='Dollar')
Country(ISO='BL', Name='Saint Barthelemy', Capital_Id=3579132, Area=21, Population=8450, Continent='NA', Currency_Code='EUR', Currency_Name='Euro')
...
"""
```

??? tips "Fonctions anonymes"

	**Pour information**, il est possible de ne pas créer de fonction dédiée au tri, mais de créer une fonction *à la volée*, une **fonction anonyme** ou **lambda fonction** pour indiquer la valeur à utiliser comme critère de tri:

    ```python
    out_sorted = sorted(out, key = lambda x:x.Area)
    for c in out_sorted:
        print(c)
    """
    Country(ISO='VA', Name='Vatican', Capital_Id=6691831, Area=0.44, Population=921, Continent='EU', Currency_Code='EUR', Currency_Name='Euro')
    Country(ISO='MC', Name='Monaco', Capital_Id=2993458, Area=1.95, Population=32965, Continent='EU', Currency_Code='EUR', Currency_Name='Euro')
    Country(ISO='GI', Name='Gibraltar', Capital_Id=2411585, Area=6.5, Population=27884, Continent='EU', Currency_Code='GIP', Currency_Name='Pound')
    Country(ISO='CC', Name='Cocos Islands', Capital_Id=7304591, Area=14, Population=628, Continent='AS', Currency_Code='AUD', Currency_Name='Dollar')
    Country(ISO='BL', Name='Saint Barthelemy', Capital_Id=3579132, Area=21, Population=8450, Continent='NA', Currency_Code='EUR', Currency_Name='Euro')
    ...
    """
    ```
	
	Il est aussi possible d'inverser l'ordre - donc d'obtenir un résultat par ordre décroissant :

    ```python
    out_sorted = sorted(out, key = lambda x:x.Area, reverse=True)
    for c in out_sorted:
        print(c)
    """
    Country(ISO='WF', Name='Wallis and Futuna', Capital_Id=4034821, Area=274, Population=16025, Continent='OC', Currency_Code='XPF', Currency_Name='Franc')
    Country(ISO='KY', Name='Cayman Islands', Capital_Id=3580661, Area=262, Population=44270, Continent='NA', Currency_Code='KYD', Currency_Name='Dollar')
    Country(ISO='KN', Name='Saint Kitts and Nevis', Capital_Id=3575551, Area=261, Population=51134, Continent='NA', Currency_Code='XCD', Currency_Name='Dollar')
    Country(ISO='NU', Name='Niue', Capital_Id=4036284, Area=260, Population=2166, Continent='OC', Currency_Code='NZD', Currency_Name='Dollar')
    Country(ISO='MO', Name='Macao', Capital_Id=1821274, Area=254, Population=449198, Continent='AS', Currency_Code='MOP', Currency_Name='Pataca')
    ...
    """
    ```

!!! question "Exercice"

	=== "Enoncé"

		1. Ecrire un code qui donne la liste des 5 états ayant la plus grande superficie, sous la forme `Nom: nom, Superficie: xxx`
		2. Ecrire un code qui donne la liste des 5 états ayant la plus petite superficie parmi les 20 états ayant la plus grande population, sous la forme `Nom: nom, population: xxx, Superficie: xxx`.
		3. Écrire les instructions permettant de d’afficher les 8 pays possédant la plus grande densité de population (habitants au km2), dans l’ordre inverse de densité décroissante, sous la forme `(Pays, population, superficie, densité)`.
		
	=== "Réponses"
    
		1. Le code :
        ```python
        for c in sorted(countries, key = lambda x:x.Area, reverse=True)[:5]:
            print( "Nom:", c.Name, ", Superficie:", c.Area )
        """
        Nom: Russia , Superficie: 17100000
        Nom: Canada , Superficie: 9984670
        Nom: United States , Superficie: 9629091
        Nom: China , Superficie: 9596960
        Nom: Brazil , Superficie: 8511965
        """
        ```
        
		2. Le code :

			```python
            out = sorted( countries, key = lambda x:x.Population, reverse=True )[:20]
            for c in sorted( out, key = lambda x:x.Area, reverse=False )[:5]:
                print( "Nom:", c.Name, ", Population:", c.Population, ", Superficie:", c.Area )
            """
            Nom: Bangladesh , Population: 156118464 , Superficie: 144000
            Nom: Philippines , Population: 99900177 , Superficie: 300000
            Nom: Vietnam , Population: 89571130 , Superficie: 329560
            Nom: Germany , Population: 81802257 , Superficie: 357021
            Nom: Japan , Population: 127288000 , Superficie: 377835
            """
			```
        
		3. Le code :
		
			```python
            out = []
            for c in countries:
                # ajoute des n-uplets non nommes
                out.append( (c.Name,c.Area,c.Population,c.Population/c.Area) )
            for c in sorted( out, key = lambda x:x[3], reverse=True )[:8]:
                print( c )
            """
            ('Monaco', 1.95, 32965, 16905.128205128207)
            ('Singapore', 692.7, 4701069, 6786.5872672152445)
            ('Hong Kong', 1092, 6898686, 6317.478021978022)
            ('Gibraltar', 6.5, 27884, 4289.846153846154)
            ('Vatican', 0.44, 921, 2093.181818181818)
            ('Sint Maarten', 21, 37429, 1782.3333333333333)
            ('Macao', 254, 449198, 1768.4960629921259)
            ('Maldives', 300, 395650, 1318.8333333333333)
            """
			```

<!--
### Fusions de tables

Le fichier `cities.csv` téléchargeable [ici](assets/cities.csv){: target="_blank"} contient une table des principales villes au niveau mondial.

!!! question "Exercice : exploration du fichier `cities.csv`"

	=== "Enoncé"

		1. Quels sont les descripteurs de ce fichier ?
		2. Ecrire un code sauvant dans une variable `cities` les enregistrements du fichiers `cities.csv`.
		3. Ecrire une boucle créant une liste donnant les villes françaises sous la forme `(Nom, population)`
		
	=== "Réponses"
	
		1. `Id;Name;Latitude;Longitude;Country_ISO;Population`
		2. Le code :

			```python
			cities = []
			with open('cities.csv', 'r', encoding='utf8', newline='') as file :
				reader = csv.DictReader(file, delimiter=";") 
				for line in reader :
					cities.append(line)
			```
		3. Le code :
		
			```python
			out = []
            for c in 
			```




Un des descripteurs est commun à la fois au fichier `countries.csv` et au fichier `cities.csv`. Il s'agit, dans `countries.csv` de `Capital_Id`, qui correspond au descripteur `Id` de `cities.csv`. Il est donc possible de joindre des données des deux tables, comme dans l'exemple ci-dessous :


```python
>>> [(co['Name'],co['Population'],co['Area'],ci['Name'], ci['Population']
) for co in countries for ci in cities if int(co['Population'])> 50*10**6 and co['Capital_Id']==ci['Id'] ]

    [('Bangladesh', '156118464', '144000', 'Dhaka', '10356500'),
     ('Brazil', '201103330', '8511965', 'Brasília', '2207718'),
     ('Democratic Republic of the Congo', '70916439', '2345410', 'Kinshasa', '7785965'),
     ('China', '1330044000', '9596960', 'Beijing', '11716620'),
     ('Germany', '81802257', '357021', 'Berlin', '3426354'),
     ('Egypt', '80471869', '1001450', 'Cairo', '7734614'),
     ('Ethiopia', '88013491', '1127127', 'Addis Ababa', '2757729'),
     ('France', '64768389', '547030', 'Paris', '2138551'),
     ('United Kingdom', '62348447', '244820', 'London', '7556900'),
     ('Indonesia', '242968342', '1919440', 'Jakarta', '8540121'),
     ('India', '1173108018', '3287590', 'Delhi', '10927986'),
     ('Iran', '76923300', '1648000', 'Tehran', '7153309'),
     ('Italy', '60340328', '301230', 'Rome', '2318895'),
     ('Japan', '127288000', '377835', 'Tokyo', '8336599'),
     ('Myanmar', '53414374', '678500', 'Nay Pyi Taw', '925000'),
     ('Mexico', '112468855', '1972550', 'Mexico City', '12294193'),
     ('Nigeria', '154000000', '923768', 'Abuja', '590400'),
     ('Philippines', '99900177', '300000', 'Manila', '1600000'),
     ('Pakistan', '184404791', '803940', 'Islamabad', '601600'),
     ('Russia', '140702000', '17100000', 'Moscow', '10381222'),
     ('Thailand', '67089500', '514000', 'Bangkok', '5104476'),
     ('Turkey', '77804122', '780580', 'Ankara', '3517182'),
     ('United States', '310232863', '9629091', 'Washington, D.C.', '601723'),
     ('Vietnam', '89571130', '329560', 'Hanoi', '1431270')]

```


!!! question "Exercice"

	=== "Enoncé"

		1. Ecrire une compréhension donnant les pays dont la population de la capitale est supérieure à 100 000.
		2. Ecrire un code donnant les pays dont la capitale possède une latitude supérieure à 60°.
		3. Ecrire un code donnant les pays dont la capitale possède une latitude inférieure à -50°.

	=== "Réponses"

		1. Le code :
		
			```python
			>>> [co['Name'] for co in countries for ci in cities if co['Capital_Id']==ci['Id'] and int(ci['Population'])> 10**5]
			```
			(La sortie est bien trop longue pour être affichée ici)
			
		2. Le code :
		
			```python
			>>> [(co['Name'],co['Population'],co['Area'],ci['Name'], ci['Population']) for co in countries for ci in cities if co['Capital_Id']==ci['Id'] and float(ci['Latitude'])> 60]
			[('Aland Islands', '26711', '1580', 'Mariehamn', '10682'),
			('Finland', '5244000', '337030', 'Helsinki', '558457'),
			('Faroe Islands', '48228', '1399', 'Tórshavn', '13200'),
			('Greenland', '56375', '2166086', 'Nuuk', '14798'),
			('Iceland', '308910', '103000', 'Reykjavík', '118918'),
			('Svalbard and Jan Mayen', '2550', '62049', 'Longyearbyen', '2060')]
			```
			
		3. Le code :

			```python
			>>> [(co['Name'],co['Population'],co['Area'],ci['Name'], ci['Population']) for co in countries for ci in cities if co['Capital_Id']==ci['Id'] and float(ci['Latitude'])<- 50]
			[('Falkland Islands', '2638', '12173', 'Stanley', '2213'),
			('South Georgia and the South Sandwich Islands',
			'30',
			'3903',
			'Grytviken',
			'2')]
			```

!!! warning "Pour les cracks : Attention !"

	La technique de fusion montrée ci-dessus n'est vraiment pas très efficace ! En effet il s'agit d'un parcours double de boucle : à chaque tour de la boucle parcourant `countries`, on parcoure **toute la liste  `cities`**. 
	
	C'est absolument horrible !
	
	En effet, si `countries` est une liste de longueur $1~000~000$ et que `cities` est une liste de taille $1~000$, alors le nombre de comparaison sera de $1~000~000 \times 1~000 = 1~000~000~000$ ! 
	
	En termes mathématiques, si `countries` est de taille $n$ et `cities` de taille $m$, alors cet algorithme aura un coût temporel en $\mathbb{O}(n\times m)$.
	
	Pour accélérer une telle fusion de liste, il peut-être judicieux de transformer ces listes en des dictionnaires, **avec un choix judicieux de clés !**. 
	
	Par exemple, ici on pourrait transformer la liste `cities` en un dictionnaire dont la clé est l'`Id`, puis effectuer une boucle sur la liste.
	
	```` python
	dicCities = {}
	for ci in cities :
			dicCities[ci['Id']] = ci
	result = []
	for co in countries :
		if int(co['Population'])> 50*10**6 :
			result.append([(co['Name'], 
							co['Population'], 
							co['Area'], 
							dicCities[co['Capital_Id']]['Name'], 
							dicCities[co['Capital_Id']]['Population']))		
	````

	Certes le code paraît plus complexe. Mais en terme de coût temporel :
	
	* Il n'y a qu'un seul parcours de la liste `cities` ;
	* A chaque tour de boucle parcourant `countries`, on ne fera appel qu'à des actions en **temps constant** (en $\mathbb{O}(1)$) sur le dictionnaire `dicCities`.
	
	En reprenant les données précédentes :
	
	* on fait $1~000$ tours de boucles pour la construction du dictionnaire ;
	* on fait $1~000~000$ de tours de boucles sur la liste `countries`.
	
	En ordre de grandeur, on reste sur environ $1~000~000$ d'opérations, soit $1~000$ fois moins que précédemment !
	
	En termes mathématiques, le coût en temps est $\mathbb{O}(max(m,n))$.
	
	Pour être encore plus clair, voici un ordre de comparaison en temps dépendant des tailles $n$ et $m$ des deux listes fusionnées, le contenu d'une case donne la comparaison en temps entre $\mathbb{O}(m \times n)$ et $\mathbb{O}(max(m,n))$, avec le principe de $1~000$ opérations par secondes.
	
	| n\m | $1$ | $10^3$ | $10^6$ | $10^9$ |
	| :---: | :---: | :---: | :---: | :---: |
	| $1$ | $0,001''~/~0,001''$  | $1''~/~1''$ | $16'40''~/~16'40''$ | $11j13h46'40''~/~11j13h46'40''$ |
	| $10^3$ | ...  | $16'40''~/~1''$ | $277h46'40''~/~16'40''$ | $\simeq 31~ans/~11j13h46'40''$ |
	| $10^6$ | ...  | ... | $\simeq 31~ans/~16'40''$ | $\simeq 31~000~années~/~11j13h46'40''$ |
	| $10^9$ | ...  | ... | ... | $\simeq 31~000~000~années~/~11j13h46'40''$ |
	
	Il y a 30 millions d'années, apparaissaient seulement les grands singes, l'Himalaya n'était pas totalement formé...
	
	Oui, direz-vous, mais les ordinateurs actuels sont 1 million de fois plus rapides !
	
	Certes, mais alors combien de temps faudrait-il dans les deux cas pour traiter deux listes de 1 milliard de données chacune ?

### Ecrire un nouveau fichier csv

Après avoir extrait, modifié et fusionné des fichiers de type `.csv`, il est normal de vouloir en créer de nouveaux à partir de données existantes. Le module `csv` propose une méthode `.DictWriter` dont l'utilisation est la suivante : 

```python
with open("capitales.csv", "w", encoding="utf8",newline="") as file :
    ##On definit les descripteurs du nouveau fichier
    descripteurs = ['Pays', 'Population_pays', 'Superficie', 'Densite', 'Capitale', 'Population_capitale']
    writer = csv.DictWriter(file, fieldnames=descripteurs,delimiter=";")

    writer.writeheader()##Ecrit les descripteurs en première ligne
    for co in countries :        
		writer.writerow({'Pays' : co['Name'],
						'Population_pays' : co['Population'],
						'Superficie' : co['Area'],
						'Densite' : float(co['Population'])/float(co['Area']),
						'Capitale' : dicCities[co['Capital_Id']]['Name'],
						'Population_Capitale' : dicCities[co['Capital_Id']]['Population']
						}
					)
```

Ainsi, on a obtenu un nouveau fichier `capitale.csv`, contenant les informations demandées.
## TP : Explorer IMDB

Le TP pour l'année 2023-2024 se fait sur Capytale par [ce lien](https://capytale2.ac-paris.fr/web/c/4630-3627353){: target = "_blank"}.

-->