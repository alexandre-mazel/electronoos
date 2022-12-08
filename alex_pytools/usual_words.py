# -*- coding: utf-8 -*-

import io
import json

import stringtools

class UsualWords:
    def __init__( self ):
        self.words = {} # words => occ
        self.maxOcc = 0 # le mot avec la plus grosse occ
        
        self.nThresholdBanal = 2000
        
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
                    
    def isWordBanal( self, w, bLookForVerb = 1 ):
        w = w.lower()
        bBanal = False
        try:
            if bLookForVerb:
                import conjugation
                conjugation.conjugator.
            occ = self.words[w]
            print("DBG: isWordBanal: %s: %s" % (w,occ))
            if occ > self.nThresholdBanal:
                bBanal = True
        except KeyError:
            print("DBG: isWordBanal: %s: not found" % (w))
        return bBanal
                    
    def filter_words( self, words ):
        """
        take a list of words and return the list of interesting words
        """
        o = []
        for w in words:
            if len(w)<3:
                continue
            if not self.isWordBanal(w):
                o.append(w)
        return o
        
    def filter_sentences( self, s ):
        """
        take a sentence and return the list of interesting words
        """
        words = stringtools.cutSentenceToWords(s)
        return self.filter_words(words)
# class UsualWords - end

usualWords = UsualWords()
usualWords.load()
s = "je suis bien d'accord"
r = usualWords.filter_sentences(s)
print("filter_sentences: %s" % r)

s = "c'est cool"
r = usualWords.filter_sentences(s)
print("filter_sentences: %s" % r)

s = "un bon petit vin rouge"
r = usualWords.filter_sentences(s)
print("filter_sentences: %s" % r)
