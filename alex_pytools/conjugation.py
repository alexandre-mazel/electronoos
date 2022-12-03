# -*- coding: cp1252 -*-

import misctools
from misctools import assert_equal

kTenseUnknown = -100
kTenseFirstTence = -2
kTensePast = -2
kTenseImperfect = -1
kTensePresent = 0
kTenseFuture = 1

class Conjugator:
    """
    conjugator for french verbs
    """
    def __init__( self ):
        pass
        
    def load( self ):
        self.aSubject = ["je", "tu", "il", "nous", "vous", "ils"]
        self.aastrTerminationByTense = [
                                    ["ai", "as", "a", "âmes", "âtes", "èrent"],
                                    ["ais", "ais", "ait", "ions", "iez", "aient"],
                                    ["e", "es", "e", "ons", "ez", "ent"],
                                    ["erai", "eras", "era", "erons", "erez", "eront"],
        ]
        
    def conjugate( self, strInf, nPers = 1, nTense = kTensePresent, bOnlyVerb = False ):
        """
        - nPers: 1: je, 2: tu, 3: il,elle, 4: nous, 5: vous, 6: ils
        - bOnlyVerb: when set => don't return subject: "aimes" instead of "tu aimes"
        """
        nPers -= 1
        group = 1 # TODO: autodetect
        if group == 1:
            radical = strInf[:-2]
            end = self.aastrTerminationByTense[nTense-kTenseFirstTence][nPers]
            lastLeter = radical[-1]
            if lastLeter == 'g' and end[0] != 'e':
                radical += 'e'
            verb = radical + end
            o = misctools.elision(self.aSubject[nPers], verb)
        return o
        
    def findInf( self, strVerb, nPers = -1 ):
        """
        find infinitive form of a conjugated verb.
        return (infinitive, pers, tense) with:
            infinitive: infinitive form of a conjugate verb
            pers: the pers 1..6
            tense: a tense in kTenseEnums
            
        - nPers: if set, will look for this persona
        """
        group = 1 # TODO: autodetect
        
        nPersFound = 0
        infinitive = "??"
        kTense = kTenseUnknown
        
        if group == 1:
            for numTense,terms in enumerate(self.aastrTerminationByTense):
                for i,term in enumerate(terms):
                    print("DBG: findInf: nPers: %s, i+1: %s" % (nPers,i+1))
                    if nPers != -1 and nPers != i+1:
                        continue
                    end = strVerb[-len(term):]
                    print("DBG: findInf: comparing '%s' and '%s'" % (term,end) )
                    if term == end:
                        nPersFound = i+1
                        infinitive = strVerb[:-len(term)]+"er"
                        kTense = numTense
                        break
        return infinitive, nPersFound,kTense+kTenseFirstTence
        
# class Conjugator - end
        
        
conjugator = Conjugator()

def autotest():
    conjugator.load()
    assert_equal(conjugator.conjugate("aimer"),"j'aime")
    assert_equal(conjugator.conjugate("manger", 2),"tu manges")
    assert_equal(conjugator.conjugate("manger", 5,kTenseFuture),"vous mangerez")
    assert_equal(conjugator.conjugate("manger", 1,kTenseImperfect),"je mangeais")
    assert_equal(conjugator.conjugate("manger", 1,kTensePast),"je mangeai")
    assert_equal(conjugator.conjugate("aimer", 1,kTensePast),"j'aimai")
    assert_equal(conjugator.conjugate("aimer", 5,kTensePast),"vous aimâtes")
    assert_equal(conjugator.conjugate("manger", 5,kTensePast),"vous mangeâtes")
    
    assert_equal(conjugator.findInf("manges"),("manger",2,kTensePresent))
    assert_equal(conjugator.findInf("mange"),("manger",1,kTensePresent))
    assert_equal(conjugator.findInf("mange",3),("manger",3,kTensePresent))
    assert_equal(conjugator.findInf("aiment"),("aimer",6,kTensePresent))
    
if __name__ == "__main__":
    autotest()