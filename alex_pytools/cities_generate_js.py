# -*- coding: utf-8 -*-

# generate a javascript list of cities

import cities_data
import stringtools

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
    # city, cp, long, lat
    allcities=cities.getAllRealCitiesAndDatas()
    txt = "citiesAndDatas=["
    for datas in allcities:
        # change t'on les accents en &eacute; oui.
        if 1:
            city, cp, long, lat = datas
            city=stringtools.accentToHtml(city)
            datas = [city, cp, long, lat]
        txt += '%s,' % str(datas)
    txt += "];"
    
output = "generated.js"
f = open(output,"wt")
f.write(txt)
f.close()
print("INF: %s generated" % output)