# -*- coding: cp1252 -*-

"""
copy to windows:
scp -P 14092 pi@thenardier.fr:/home/pi/save/temperature.txt c:\save\temperature_thenardier.txt
"""

import io
import os
import random
import sys
import time

sys.path.append("../alex_pytools/")
import misctools
import nettools
import stringtools

def store(city,temp,cond):
    timestamp = misctools.getTimeStamp()
    if os.name == "nt":
        dest = "c:/save/temperature.txt"
    else:
        dest = os.path.expanduser("~/save/temperature.txt")
    
    f = open(dest,"a")
    f.write("%s: %s: %s: %s\n" % (timestamp,city,temp,cond) )
    f.close()

# from https://weather.com
def retrieveTemp():
    startbase = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--MHmYY">'
    startbase = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--MHmYY" dir="ltr">'
    startbase = '<span data-testid="TemperatureValue" class="CurrentConditions--tempValue--zUBSz" dir="ltr">'
    stopbase = "�</span>"
    # beau: soleil avec des nuages, ensolleile: plein soleil
    astrDatas = [
            ["Paris", "https://weather.com/fr-FR/temps/aujour/l/48.86,2.35?par=google",startbase,stopbase],
            ["Le Kremlin-Bicetre", "https://weather.com/fr-FR/temps/aujour/l/ccb7b6dc48e255339753562e6a8ea1b48b796d68cc275ef58b3d8fe4c9b75fa7",startbase,stopbase],
            ["Beziers", "https://weather.com/fr-FR/temps/aujour/l/48dfaf8b4db3509a7e858c54a0ec35164fa8baccc73b35f6b9e0cd04b7544ea5",startbase,stopbase],
            ["Bort-les-Orgues", "https://weather.com/fr-FR/temps/aujour/l/14e53d3cef725e41222474317acf1d27951992d718300074c36ded62883afdd5",startbase,stopbase],
            ["Saint-bonnet-pret-bort", "https://weather.com/fr-FR/temps/aujour/l/356a10c392837b0bd6f3e7ddd33acb4d385701ddf07ebae91c8ed2fa8b7c803c",startbase,stopbase],
            ["Annecy", "https://weather.com/fr-FR/temps/aujour/l/dca69ee3f92301838c6a8f09e67796bf14fe8684fb90ed81dc4cbfb732668169",startbase,stopbase],
            ["Biarritz", "https://weather.com/fr-FR/temps/aujour/l/ad456d1b2d0a43d1e8940f2f0f6956ff227ebe4f5faf3f0af67e22f17242a9a2",startbase,stopbase],
            ["Vacheres", "https://weather.com/fr-FR/temps/aujour/l/0e75f3a11bcabc16a92fe0d2e9924db5630544cf77e2aa76c11cfe7069313825",startbase,stopbase],
            ["St Malo", "https://weather.com/fr-FR/temps/aujour/l/a1baaf192d861ad1bed879b83a55048b51283588728dfbcf6dc28281d5ce8f4f",startbase,stopbase],
            ["Bordeaux", "https://weather.com/fr-FR/temps/aujour/l/12fae739549c2bb1e6693bdb14c062671c7c87d40051273a05a4eaf5848064fe",startbase,stopbase],
            ["Tavira", "https://weather.com/fr-FR/temps/aujour/l/efa3db97660e2aaaa3efc076350dd00386e0453da1547361cd68e78a412f2fb8",startbase,stopbase],  # 1890 du kb, 1432 de nissan
            ["VN Gaia", "https://weather.com/fr-FR/temps/aujour/l/7291c492bc9efb63e5a06ee49112469d08890e36e59bc3df64648f4c681440d5",startbase,stopbase],  # 1578 du kb, 1274 de nissan
            ["Las Palmas", "https://weather.com/fr-FR/temps/aujour/l/9e18ab8b60528d5a8feb814d67eaf1bcf4dbadaeff6525ac3bd8441f91152ddf",startbase,stopbase],
            ["Catanzaro", "https://weather.com/fr-FR/temps/aujour/l/3f280c709bf4c7f0a8fa089a6330d319a5b8d98621e2aa59cd0615a61d1422fb",startbase,stopbase], # 2034 du kb, 1678 de nissan
            ["Bonifacio", "https://weather.com/fr-FR/temps/aujour/l/d239e6e08b72ecddf56b42b9dde7ff0b1a3dc6a02f263523504e905d66e78748",startbase,stopbase],
            ["Pachino", "https://weather.com/fr-FR/temps/aujour/l/141fff9553992cdbb6063546facc1ba6c182c5a0a806c99e7ba408b37c4f80cb",startbase,stopbase],
    ]
    
    start_cond = '<div data-testid="wxPhrase" class="CurrentConditions--phraseValue--mZC_p">'
    start_cond = '<div data-testid="wxPhrase" class="CurrentConditions--phraseValue---VS-k">'
    stop_cond = '</div><div class="CurrentConditions--tempHiLoValue--3T1DG">'
    stop_cond = '</div><div class="CurrentConditions--tempHiLoValue--Og9IG">'
    
    for city,link,txt_start,txt_end in astrDatas:
        dst = "/tmp/meteo_temp.html"
        nettools.download(link,dst,bForceDownload=1)
        f = io.open(dst,"r",encoding='utf-8')
        buf = f.read()
        f.close()
        temp = stringtools.findSubString(buf,txt_start,txt_end)
        cond = stringtools.findSubString(buf,start_cond,stop_cond)
        # beau: soleil avec un peu de nuage
        # ensoleill�: plein soleil
        
        if len(temp)>4:
            # recemment il reste un tag dans la temp, on l'enleve.
            idx = temp.find('<')
            if idx != -1:
                temp = temp[:idx]
        print("DBG: retrieveTemp: %s: temp: '%s' cond: '%s'" % (city,temp,cond) )
        try:
            if len(temp) < 3:
                temp = int(temp)
                cond = cond.replace("�","e")
                store(city,temp,cond)
        except BaseException as err:
            print("ERR: retrieveTemp: during store, err: %s" % err )
        time.sleep(random.random()*10)
        time.sleep(8)
        #~ break
            
# retrieveTemp - end

def loop(nTimeLoopMin=14):
    while 1:
        retrieveTemp()
        print("sleeping %d min..." % nTimeLoopMin)
        time.sleep(nTimeLoopMin*60)
        #~ use misctools.isQuarterHour ?

#~ retrieveTemp()
loop()

