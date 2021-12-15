# -*- coding: utf-8 -*-

# generate a javascript list of cities

import cities_data

cities = cities_data.Cities()
cities.load()

if 0:
    # juste city and cp in one string
    allcities=cities.getAllRealCitiesName(True)
    txt = "cities=["
    for city in allcities:
        txt += '"%s",' % city
    txt += "];"
else:
    allcities=cities.getAllRealCitiesAndDatas()
    txt = "citiesAndDatas=["
    for city in allcities:
        txt += '%s,' % city
    txt += "];"
    
output = "generated.js"
f = open(output,"wt")
f.write(txt)
f.close()
print("INF: %s generated" % output)