# -*- coding: cp1252 -*-

import misctools
from misctools import assert_equal

kTenseUnknown = -100
kTenseFirst = -2
kTensePast = -2
kTenseImperfect = -1
kTensePresent = 0
kTenseFuture = 1
kTenseMax = 2

libTense = ["Past","Imperfect","Present","Future"]
def tenseToStr(k):
    return libTense[k-kTenseFirst]
    

class Conjugator:
    """
    conjugator for french verbs
    """
    def __init__( self ):
        pass
        
    def load( self ):
        self.aSubject = ["je", "tu", "il", "nous", "vous", "ils"]
        self.aaastrTerminationByTense = [
                            [ # 1st
                                    ["ai", "as", "a", "âmes", "âtes", "èrent"],
                                    ["ais", "ais", "ait", "ions", "iez", "aient"],
                                    ["e", "es", "e", "ons", "ez", "ent"],
                                    ["erai", "eras", "era", "erons", "erez", "eront"],
                            ],
                            [ # 2
                                    ["is", "is", "it", "îmes", "îtes", "irent"],
                                    ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                    ["is", "is", "it", "issons", "issez", "issent"],
                                    ["irai", "iras", "ira", "irons", "irez", "iront"],
                            ],
                            [ # 3
                                    ["is", "is", "it", "îmes", "îtes", "irent"],
                                    ["enais", "enais", "enait", "enions", "eniez", "enaient"],
                                    ["ends", "ends", "end", "enons", "enez", "ennent"],
                                    ["endrai", "endras", "endra", "endrons", "endrez", "endront"],
                            ],
        ]
        
        self.aaParticular = {
            "être":      [
                                    ["fus", "fus", "fut", "fûmes", "fûtes", "furent"],
                                    ["étais", "étais", "était", "étions", "étiez", "étaient"],
                                    ["suis", "es", "est", "sommes", "êtes", "sont"],
                                    ["serai", "seras", "sera", "serons", "serez", "seront"],
                            ],
            "avoir":      [
                                    ["eus", "eus", "eut", "eûmes", "eûtes", "eurent"],
                                    ["avais", "avais", "avait", "avions", "aviez", "avaient"],
                                    ["ai", "as", "a", "avons", "avez", "ont"],
                                    ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
                            ],
        }
        
        self.aaParticularTrois = {
            "oire":      [
                                    ["us", "us", "ut", "ûmes", "ûtes", "urent"],
                                    ["oyais", "oyais", "oyait", "oyions", "oyiez", "oyaient"],
                                    ["ois", "ois", "oit", "oyons", "oyez", "oient"],
                                    ["oirai", "oiras", "oira", "oirons", "oirez", "oiront"],
                            ],
            "oitre":      [
                                    ["ûs", "ûs", "ût", "ûmes", "ûtes", "ûrent"],
                                    ["oissais", "oissais", "oissait", "oissions", "oissiez", "oissaient"],
                                    ["oîs", "oîs", "oît", "oissons", "oissez", "oissent"],
                                    ["oîtrai", "oîtras", "oîtra", "oîtrons", "oîtrez", "oîtront"],
                            ],
        }
        
    def detectGroup( self, strInf ):
        if strInf[-2:] == 'er':
            if strInf != "aller":
                return 1
            return 3
        if strInf[-3:] in ['dre','tre','oir'] :
            return 3
        if strInf[-4:] in ['oire']:
            return 3
        return 2
        
    def conjugate( self, strInf, nPers = 1, nTense = kTensePresent, bOnlyVerb = False ):
        """
        - nPers: 1: je, 2: tu, 3: il,elle, 4: nous, 5: vous, 6: ils
        - bOnlyVerb: when set => don't return subject: "aimes" instead of "tu aimes"
        """
        bVerbose = 1
        bVerbose = 0
        
        nPers -= 1
        group = self.detectGroup(strInf)

        try:
            verb = self.aaParticular[strInf][nTense-kTenseFirst][nPers]
        except KeyError as err:
            radical = strInf[:-2]
            end = self.aaastrTerminationByTense[group-1][nTense-kTenseFirst][nPers]
            if group == 3:
                bOire = strInf[-4:] in ['oire'] # croire style
                bOitre = strInf[-5:] in ['oitre','oître'] # croitre style
                if bOire:
                    radical = strInf[:-4]
                    end = self.aaParticularTrois[strInf[-4:]][nTense-kTenseFirst][nPers]
                elif bOitre:
                    radical = strInf[:-5]
                    end = self.aaParticularTrois['oitre'][nTense-kTenseFirst][nPers]
                elif len(strInf)>4:
                    radical = strInf[:-5]
            if bVerbose: print("DBG: conjugate: radical: '%s'" % radical )
            lastLeter = radical[-1]
            if lastLeter == 'g' and end[0] not in['e','é', 'è','i']:
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
        bVerbose = 1
        bVerbose = 0
            
        group = 1 # TODO: autodetect, mais comment?
        
        nPersFound = 0
        infinitive = "??"
        kTense = kTenseUnknown
        
        bFound = 0
        if group == 1:
            #~ for numTense,terms in enumerate(self.aaastrTerminationByTense): # probleme pour différencier futur et present, donc on commence par le futur
            for numTense in [kTenseFuture,kTenseImperfect,kTensePast,kTensePresent]: # not optimal in sense of frequency but works better in this order               
                numTense -=kTenseFirst
                terms = self.aaastrTerminationByTense[group-1][numTense]
                if bFound: break
                for i,term in enumerate(terms):
                    if bVerbose: print("DBG: findInf: nPers: %s, i+1: %s" % (nPers,i+1))
                    if nPers != -1 and nPers != i+1:
                        continue
                    end = strVerb[-len(term):]
                    if bVerbose: print("DBG: findInf: comparing '%s' and '%s'" % (term,end) )
                    if term == end:
                        if bVerbose: print("DBG: findInf: hit")
                        nPersFound = i+1
                        infinitive = strVerb[:-len(term)]
                        if infinitive[-1] != 'e':
                            infinitive += 'e'
                        infinitive += 'r'
                        kTense = numTense
                        bFound = 1
                        break
        return infinitive, nPersFound,kTense+kTenseFirst
        
    def printAllConjugaison(self,verb):
        print("*** Conjugaison du verbe %s ***" % verb)
        for tense in range(kTenseFirst,kTenseMax):
            print("%s:" % tenseToStr(tense))
            for i,subject in enumerate(self.aSubject):
                print("    " + self.conjugate(verb,i+1,tense))
            print("")
        
# class Conjugator - end

        
        
conjugator = Conjugator()

def autotest():
    conjugator.load()
    
    # 1er groupe
    assert_equal(conjugator.detectGroup("aimer"),1)
    assert_equal(conjugator.conjugate("aimer"),"j'aime")
    assert_equal(conjugator.conjugate("manger", 2),"tu manges")
    assert_equal(conjugator.conjugate("manger", 5,kTenseFuture),"vous mangerez")
    assert_equal(conjugator.conjugate("manger", 1,kTenseImperfect),"je mangeais")
    assert_equal(conjugator.conjugate("manger", 1,kTensePast),"je mangeai")
    assert_equal(conjugator.conjugate("aimer", 1,kTensePast),"j'aimai")
    assert_equal(conjugator.conjugate("aimer", 5,kTensePast),"vous aimâtes")
    assert_equal(conjugator.conjugate("manger", 5,kTensePast),"vous mangeâtes")
    assert_equal(conjugator.conjugate("manger", 6,kTensePast),"ils mangèrent")
    
    assert_equal(conjugator.findInf("manges"),("manger",2,kTensePresent))
    assert_equal(conjugator.findInf("mange"),("manger",1,kTensePresent))
    assert_equal(conjugator.findInf("mange",3),("manger",3,kTensePresent))
    assert_equal(conjugator.findInf("aiment"),("aimer",6,kTensePresent))
    assert_equal(conjugator.findInf("mangeâtes"),("manger",5,kTensePast))
    assert_equal(conjugator.findInf("mangerons"),("manger",4,kTenseFuture)) # ne fonctionne pas: verbe mangerer !?!
    assert_equal(conjugator.findInf("porterons"),("porter",4,kTenseFuture)) # ne fonctionne pas: verbe porterer !?!
    
    # 2iemegroupe
    assert_equal(conjugator.detectGroup("finir"),2)
    assert_equal(conjugator.conjugate("finir"),"je finis")
    assert_equal(conjugator.conjugate("finir", 2),"tu finis")
    assert_equal(conjugator.conjugate("finir", 3),"il finit")
    assert_equal(conjugator.conjugate("finir", 4),"nous finissons")
    assert_equal(conjugator.conjugate("finir", 5),"vous finissez")
    assert_equal(conjugator.conjugate("finir", 6),"ils finissent")
    assert_equal(conjugator.conjugate("finir", 5,kTenseFuture),"vous finirez")
    assert_equal(conjugator.conjugate("finir", 1,kTenseImperfect),"je finissais")
    assert_equal(conjugator.conjugate("finir", 1,kTensePast),"je finis")
    assert_equal(conjugator.conjugate("finir", 5,kTensePast),"vous finîtes")
    assert_equal(conjugator.conjugate("finir", 6,kTensePast),"ils finirent")
    
    # 3iemegroupe
    assert_equal(conjugator.detectGroup("prendre"),3)
    assert_equal(conjugator.detectGroup("croire"),3)
    assert_equal(conjugator.detectGroup("croitre"),3)
    assert_equal(conjugator.detectGroup("croître"),3)
    assert_equal(conjugator.detectGroup("croitre"),3)
    assert_equal(conjugator.detectGroup("être"),3)
    assert_equal(conjugator.detectGroup("avoir"),3)
    
    assert_equal(conjugator.conjugate("prendre"),"je prends")
    assert_equal(conjugator.conjugate("prendre", 2),"tu prends")
    assert_equal(conjugator.conjugate("prendre", 3),"il prend")
    assert_equal(conjugator.conjugate("prendre", 4),"nous prenons")
    assert_equal(conjugator.conjugate("prendre", 5),"vous prenez")
    assert_equal(conjugator.conjugate("prendre", 6),"ils prennent")
    
    assert_equal(conjugator.conjugate("croire"),"je crois")
    assert_equal(conjugator.conjugate("croire", 2),"tu crois")
    assert_equal(conjugator.conjugate("croire", 3),"il croit")
    assert_equal(conjugator.conjugate("croire", 4),"nous croyons")
    assert_equal(conjugator.conjugate("croire", 5),"vous croyez")
    assert_equal(conjugator.conjugate("croire", 6),"ils croient")
    assert_equal(conjugator.conjugate("croire", 5,kTenseFuture),"vous croirez")
    assert_equal(conjugator.conjugate("croire", 1,kTenseImperfect),"je croyais")
    assert_equal(conjugator.conjugate("croire", 1,kTensePast),"je crus")
    assert_equal(conjugator.conjugate("croire", 5,kTensePast),"vous crûtes")
    assert_equal(conjugator.conjugate("croire", 6,kTensePast),"ils crurent")
    
    # compliqué:
    assert_equal(conjugator.conjugate("croître"),"je croîs")
    assert_equal(conjugator.conjugate("croître", 1,kTenseFuture),"je croîtrai")
    assert_equal(conjugator.conjugate("croître", 1,kTensePast),"je crûs")
    assert_equal(conjugator.conjugate("croître", 1,kTenseImperfect),"je croissais")
    
    assert_equal(conjugator.conjugate("être"),"je suis")
    assert_equal(conjugator.conjugate("être", 2),"tu es")
    assert_equal(conjugator.conjugate("être", 3),"il est")
    assert_equal(conjugator.conjugate("être", 4),"nous sommes")
    assert_equal(conjugator.conjugate("être", 5),"vous êtes")
    assert_equal(conjugator.conjugate("être", 6),"ils sont")
    assert_equal(conjugator.conjugate("être", 1,kTenseFuture),"je serai")
    assert_equal(conjugator.conjugate("être", 1,kTensePast),"je fus")
    assert_equal(conjugator.conjugate("être", 1,kTenseImperfect),"j'étais")
    
    assert_equal(conjugator.conjugate("avoir"),"j'ai")
    assert_equal(conjugator.conjugate("avoir", 2),"tu as")
    assert_equal(conjugator.conjugate("avoir", 3),"il a")
    assert_equal(conjugator.conjugate("avoir", 4),"nous avons")
    assert_equal(conjugator.conjugate("avoir", 5),"vous avez")
    assert_equal(conjugator.conjugate("avoir", 6),"ils ont")
    assert_equal(conjugator.conjugate("avoir", 1,kTenseFuture),"j'aurai")
    assert_equal(conjugator.conjugate("avoir", 1,kTensePast),"j'eus")
    assert_equal(conjugator.conjugate("avoir", 1,kTenseImperfect),"j'avais")
    assert_equal(conjugator.conjugate("avoir", 4,kTenseFuture),"nous aurons")
    assert_equal(conjugator.conjugate("avoir", 4,kTensePast),"nous eûmes")
    assert_equal(conjugator.conjugate("avoir", 4,kTenseImperfect),"nous avions")
    
    print("")
    conjugator.printAllConjugaison("aimer")
    conjugator.printAllConjugaison("manger")
    conjugator.printAllConjugaison("finir")
    conjugator.printAllConjugaison("prendre")
    conjugator.printAllConjugaison("croire")
    conjugator.printAllConjugaison("croître")

    conjugator.printAllConjugaison("être")
    conjugator.printAllConjugaison("avoir")
    
if __name__ == "__main__":
    autotest()