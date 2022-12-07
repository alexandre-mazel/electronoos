# -*- coding: utf-8 -*-

import io
import json

with io.open('datas/words_frequency_fr.json', encoding="utf8") as dataFile:
    data = dataFile.read()
    #~ obj = data[data.find('{') : data.rfind('}')+1]
    jsonObj = json.loads(data)
    print(jsonObj)
    for obj in jsonObj[:20]:
        print("%s: %d" % (obj["label"],obj["frequency"]))