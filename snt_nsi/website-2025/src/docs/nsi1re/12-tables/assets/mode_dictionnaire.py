import csv

# Lecture du fichier CSV
fichier = open('jo_beijing_2022.csv')
medailles = list(csv.DictReader(fichier, delimiter=','))
fichier.close()

# Filtrage des lignes
medailles_or = []

for i in range(len(medailles)):
    if int(medailles[i]['or']) > 0:
        medailles_or.append(medailles[i])

# Filtrage des colonnes
pays = []

for i in range(len(medailles_or)):
    pays.append({'pays': medailles_or[i]['pays'], 'or': medailles_or[i]['or']})


# Tri du tableau
def trier_par_medaille(ligne):
    return int(ligne['or'])


pays.sort(key=trier_par_medaille, reverse=True)

# Écriture des données dans un nouveau fichier CSV
fichier = open('medailles_or.csv', 'w')

w = csv.DictWriter(fichier, fieldnames=['pays', 'or'])
w.writeheader()
w.writerows(pays)

fichier.close()
