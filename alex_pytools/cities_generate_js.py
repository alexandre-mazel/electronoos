# -*- coding: utf-8 -*-

# generate a javascript list of cities

import cities_data
import stringtools

def generate_cities_js():
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
        
    output = "generated_cities.js"
    f = open(output,"wt")
    f.write(txt)
    f.close()
    print("INF: %s generated" % output)
    
# generate_cities_js - end

def generate_dept_js():
    r = cities_data.Regions()
    r.load()

    txt = "deptAndDatas=["
    for num_dept,v in r.dictDeptByNumber.items():
        # change t'on les accents en &eacute; oui.
        if 1:
            strName = stringtools.accentToHtml(v)
            datas = [strName,num_dept]
        txt += '%s,' % str(datas)
    txt += "];"
        
    output = "generated_dept.js"
    f = open(output,"wt")
    f.write(txt)
    f.close()
    print("INF: %s generated" % output)
    
# generate_cities_js - end

#~ generate_cities_js()
generate_dept_js()
