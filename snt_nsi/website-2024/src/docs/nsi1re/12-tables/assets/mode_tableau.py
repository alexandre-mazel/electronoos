import csv

# Lecture du fichier CSV
fichier = open('jo_beijing_2022.csv')
medailles = list(csv.reader(fichier))
fichier.close()

# Filtrage des lignes
medailles_or = []

for i in range(1, len(medailles)):
    if int(medailles[i][1]) > 0:
        medailles_or.append(medailles[i])

# Filtrage des colonnes
pays = []

for i in range(len(medailles_or)):
    pays.append([medailles_or[i][0], medailles_or[i][1]])


# Tri du tableau
def trier_par_medaille(ligne):
    return int(ligne[1])


pays.sort(key=trier_par_medaille, reverse=True)

# Écriture des données dans un nouveau fichier CSV
fichier = open('medailles_or.csv', 'w')

w = csv.writer(fichier)
w.writerow(['pays', 'or'])
w.writerows(pays)

fichier.close()
