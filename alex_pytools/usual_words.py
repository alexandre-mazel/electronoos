# -*- coding: utf-8 -*-

import io
import json

class UsualWords:
    def __init__( self ):
        self.words = {} # words => occ
        self.maxOcc = 0 # le mot avec la plus grosse occ
        
    def load( self ):
        with io.open('datas/words_frequency_fr.json', encoding="cp1252") as dataFile:
            data = dataFile.read()
            #~ obj = data[data.find('{') : data.rfind('}')+1]
            jsonObj = json.loads(data)
            #~ print(jsonObj)
            self.maxOcc = jsonObj[0]["frequency"]
            for cpt,obj in enumerate(jsonObj):
                w = obj["label"]
                occ = obj["frequency"]
                self.words[w] = occ
                if cpt < 20:
                    print("%s: %d" % (w,occ))
# class UsualWords - end
usualWords = UsualWords()
usualWords.load()