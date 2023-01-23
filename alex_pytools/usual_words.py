# -*- coding: utf8 -*-

import io
import json
import sys

import misctools
from misctools import assert_equal
import stringtools

class UsualWords:
    def __init__( self ):
        self.words = {} # words => occ
        self.maxOcc = 0 # le mot avec la plus grosse occ
        
        self.nThresholdBanal = 3200 # si on veut garder travailler on doit etre au dessus de 3133
        
    def load( self ):
        with io.open(misctools.getThisFilePath()+'datas/words_frequency_fr.json', encoding="utf8") as dataFile:
            data = dataFile.read()
            #~ obj = data[data.find('{') : data.rfind('}')+1]
            jsonObj = json.loads(data)
            #~ print(jsonObj)
            self.maxOcc = jsonObj[0]["frequency"]
            print("DBG: UsualWords: print 20 most frequent(s):")
            for cpt,obj in enumerate(jsonObj):
                w = obj["label"]
                occ = obj["frequency"]
                self.words[w] = occ
                if sys.version_info[0] >= 3:
                    if cpt < 20:
                        print("%s: %d" % (w,occ))
                    
        # add banal word who should be there:
        listAdd = [
                "les", "des","un", "une", "le","la",
                "suis","es","est","sommes", "sont",
                "mon", "ton", "son",
                # congugate verb (should be detected when looking for verb, but doesn't work well)
                "dis","faudrait", "connais"
        ]
        for w in listAdd:
            self.words[w] = 100000
        
                    
    def isWordBanal( self, w, bLookForVerb = 1, bVerbose = False ):
        w = w.lower()
        bBanal = False
        try:
            occ = self.words[w]
            if bVerbose: print("DBG: isWordBanal: %s: %s" % (w,occ))
            if occ > self.nThresholdBanal:
                bBanal = True
        except KeyError:
            if bVerbose: print("DBG: isWordBanal: %s: not found" % (w))
        if not bBanal:
            if bLookForVerb:
                import conjugation
                infi = conjugation.conjugator.findInf(w)[0]
                if bVerbose: print("DBG: isWordBanal: found infinitive: '%s' => '%s'" % (w,infi) )
                if infi != "" and self.isWordBanal(infi,bVerbose=bVerbose):
                    return True
        return bBanal
                    
    def filter_words( self, words, bLookForVerb = True, bVerbose = False ):
        """
        take a list of words and return the list of interesting words
        """
        o = []
        for w in words:
            if len(w)<3:
                continue
            if not self.isWordBanal(w,bLookForVerb=bLookForVerb,bVerbose=bVerbose):
                o.append(w)
        return o
        
    def filter_sentences( self, s, bLookForVerb = True, bVerbose = False ):
        """
        take a sentence and return the list of interesting words
        """
        words = stringtools.cutSentenceToWords(s)
        return self.filter_words(words,bLookForVerb=bLookForVerb,bVerbose=bVerbose)
# class UsualWords - end

usualWords = UsualWords()
usualWords.load()

def isUsualWord(w,bLookForVerb = 1, bVerbose = False):
    return usualWords.isWordBanal(w,bLookForVerb=bLookForVerb,bVerbose=bVerbose)
    
def filterSentences(w,bLookForVerb = 1, bVerbose = False):
    return usualWords.filter_sentences(w,bLookForVerb=bLookForVerb,bVerbose=bVerbose)

def autoTest():
    assert_equal( isUsualWord("je"),1)
    assert_equal( isUsualWord("jE"),1)
    assert_equal( isUsualWord("Avoir"),1)
    assert_equal( isUsualWord("être"),1)
    assert_equal( isUsualWord("suis"),1)
    assert_equal( isUsualWord("Alexandre"),0)
    assert_equal( isUsualWord("les"),1)
    assert_equal( isUsualWord("des"),1)
    assert_equal( isUsualWord("le"),1)
    assert_equal( isUsualWord("la"),1)
    assert_equal( isUsualWord("de"),1)
    assert_equal( isUsualWord("un"),1)
    assert_equal( isUsualWord("une"),1)
    assert_equal( isUsualWord("suis"),1)
    assert_equal( isUsualWord("es"),1)
    assert_equal( isUsualWord("est"),1)
    assert_equal( isUsualWord("sommes"),1)
    assert_equal( isUsualWord("sont"),1)
    assert_equal( isUsualWord("mon"),1)
    assert_equal( isUsualWord("ton"),1)
    assert_equal( isUsualWord("son"),1)
    assert_equal( isUsualWord("dis"),1)


if __name__ == "__main__":
    autoTest()

    s = "je suis bien d'accord"
    r = usualWords.filter_sentences(s)
    print("filter_sentences: '%s' => %s" % (s,r))

    s = "c'est cool"
    r = usualWords.filter_sentences(s)
    print("filter_sentences: '%s' => %s" % (s,r))

    s = "Un bon petit Vin Rouge"
    r = usualWords.filter_sentences(s)
    print("filter_sentences: '%s' => %s" % (s,r))
