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
                                    ["ai", "as", "a", "�mes", "�tes", "�rent"],
                                    ["ais", "ais", "ait", "ions", "iez", "aient"],
                                    ["e", "es", "e", "ons", "ez", "ent"],
                                    ["erai", "eras", "era", "erons", "erez", "eront"],
                            ],
                            [ # 2
                                    ["is", "is", "it", "�mes", "�tes", "irent"],
                                    ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                    ["is", "is", "it", "issons", "issez", "issent"],
                                    ["irai", "iras", "ira", "irons", "irez", "iront"],
                            ],
                            [ # 3
                                    ["is", "is", "it", "�mes", "�tes", "irent"],
                                    ["enais", "enais", "enait", "enions", "eniez", "enaient"],
                                    ["ends", "ends", "end", "enons", "enez", "ennent"],
                                    ["endrai", "endras", "endra", "endrons", "endrez", "endront"],
                            ],
        ]
        
        self.aaParticular = {
            "�tre":      [
                                    ["fus", "fus", "fut", "f�mes", "f�tes", "furent"],
                                    ["�tais", "�tais", "�tait", "�tions", "�tiez", "�taient"],
                                    ["suis", "es", "est", "sommes", "�tes", "sont"],
                                    ["serai", "seras", "sera", "serons", "serez", "seront"],
                            ],
            "avoir":      [
                                    ["eus", "eus", "eut", "e�mes", "e�tes", "eurent"],
                                    ["avais", "avais", "avait", "avions", "aviez", "avaient"],
                                    ["ai", "as", "a", "avons", "avez", "ont"],
                                    ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
                            ],
        }
        
        self.aaParticularTrois = {
            "aire":      [
                                    ["is", "is", "it", "�mes", "�tes", "irent"],
                                    ["aisais", "aisais", "aisait", "aisions", "aisiez", "aisaient"],
                                    ["ais", "ais", "ait", "aisons", "aites", "ont"],
                                    ["erai", "eras", "era", "erons", "erez", "eront"],
                            ],
            "oire":      [
                                    ["us", "us", "ut", "�mes", "�tes", "urent"],
                                    ["oyais", "oyais", "oyait", "oyions", "oyiez", "oyaient"],
                                    ["ois", "ois", "oit", "oyons", "oyez", "oient"],
                                    ["oirai", "oiras", "oira", "oirons", "oirez", "oiront"],
                            ],
            "oitre":      [
                                    ["�s", "�s", "�t", "�mes", "�tes", "�rent"],
                                    ["oissais", "oissais", "oissait", "oissions", "oissiez", "oissaient"],
                                    ["o�s", "o�s", "o�t", "oissons", "oissez", "oissent"],
                                    ["o�trai", "o�tras", "o�tra", "o�trons", "o�trez", "o�tront"],
                            ],
        }
        
    def detectGroup( self, strInf ):
        if strInf[-2:] == 'er':
            if strInf != "aller":
                return 1
            return 3
        if strInf[-3:] in ['dre','tre','oir'] :
            return 3
        if strInf[-4:] in ['oire','aire']:
            return 3
        return 2
        
    def conjugate( self, strInf, nPers = 1, nTense = kTensePresent, bOnlyVerb = False ):
        """
        - nPers: 1: je, 2: tu, 3: il,elle, 4: nous, 5: vous, 6: ils
        - bOnlyVerb: when set => omit subject:  return "aimes" instead of "tu aimes"
        return "" if fail to conjugate
        """
        bVerbose = 1
        bVerbose = 0
        
        nPers -= 1
        group = self.detectGroup(strInf)

        try:
            verb = self.aaParticular[strInf][nTense-kTenseFirst][nPers]
        except KeyError as err:
            radical = strInf[:-2]
            if radical == '':
                return ''
            end = self.aaastrTerminationByTense[group-1][nTense-kTenseFirst][nPers]
            if group == 3:
                bOire = strInf[-4:] in ['oire','aire'] # croire style
                bOitre = strInf[-5:] in ['oitre','o�tre'] # croitre style
                if bOire:
                    radical = strInf[:-4]
                    end = self.aaParticularTrois[strInf[-4:]][nTense-kTenseFirst][nPers]
                elif bOitre:
                    radical = strInf[:-5]
                    end = self.aaParticularTrois['oitre'][nTense-kTenseFirst][nPers]
                elif len(strInf)>4:
                    radical = strInf[:-5]
            if bVerbose: print("DBG: conjugate: radical: '%s'" % radical )
            if radical == '':
                return ''
            lastLeter = radical[-1]
            if lastLeter == 'g' and end[0] not in['e','�', '�','i']:
                radical += 'e'
            verb = radical + end
        
        if bOnlyVerb:
            return verb
        
        o = misctools.elision(self.aSubject[nPers], verb)

        return o
        
    def findInf( self, strVerb, nPers = -1 ):
        """
        find infinitive form of a conjugated verb.
        return (infinitive, pers, tense) with:
            infinitive: infinitive form of a conjugate verb
            pers: the pers 1..6
            tense: a tense in kTenseEnums
        return ("",0,0) if not found
            
        - nPers: if set, will look for this persona
        """
        
        # N'aurait on pas presque plus vite fait de generer tout les verbes du monde et de faire un lookup ?
        # ca fait peut etre un peu beaucoup quand meme...
        
        bVerbose = 1
        bVerbose = 0
            
        group = 1 # TODO: autodetect, mais comment?
        
        nPersFound = 0
        infinitive = ""
        kTense = kTenseUnknown
        
        # range(self.aaastrTerminationByTense): # probleme pour diff�rencier futur et present, donc on commence par le futur
        listTense = [kTenseFuture,kTenseImperfect,kTensePast,kTensePresent] # not optimal in sense of frequency but works better in this order               
        
        # look for peculiar
        for infi,tenses in self.aaParticular.items():             
            for numTense,forms in enumerate(tenses):
                for pers in range(1,7):
                    if nPers != -1 and pers != nPers:
                        continue
                    if bVerbose: print("DBG: findInf: aaParticular: comparing %s and %s" % (strVerb,forms[pers-1]) )
                    if strVerb == forms[pers-1]:
                        return infi,pers,numTense+kTenseFirst

        
        bFound = 0
        for group in range(3,0,-1): # start by longer and more specific one
            if bFound: break
            if bVerbose: print("DBG: findInf: * group: %d" % group )
            for numTense in listTense:
                numTense -=kTenseFirst
                terms = self.aaastrTerminationByTense[group-1][numTense]
                if bFound: break
                for i,term in enumerate(terms):
                    if bVerbose: print("DBG: findInf: nPers: %s, i+1: %s" % (nPers,i+1))
                    if nPers != -1 and nPers != i+1:
                        continue
                    end = strVerb[-len(term):]
                    if bVerbose: print("DBG: findInf: comparing '%s' and '%s'" % (end,term) )
                    if term == end:
                        if bVerbose: print("DBG: findInf: hit")
                        nPersToCheck = i+1
                        infi = strVerb[:-len(term)]
                        if infi == '':
                            continue
                        if bVerbose: print("DBG: findInf: look for infinitive group %d using '%s'" % (group,infi) )
                        if group == 1:
                            if (len(infi)> 0 and infi[-1] == 'y' ) or (len(infi)> 1 and infi[-2] == 'y'):
                                # peu probable!
                                continue
                            if infi[-1] != 'e':
                                infi += 'e'
                            infi += 'r'
                        elif group == 2:
                            if infi[-1] != 'i':
                                infi += 'i'
                            infi += 'r'
                        else:
                            if infi[-1] == 'a':
                                infi = infi[:-1] + 'e'
                            else:
                                #trop de cas particulier � venir...
                                if infi[-1] == 'r':
                                    infi += "endre"
                                else:
                                    infi += "aire"
                        
                        check = self.conjugate(infi,nPersToCheck,numTense+kTenseFirst,bOnlyVerb=True)
                        if check != strVerb:
                            if bVerbose: print("DBG: findInf: check for verb '%s', fail: %s != %s" % (infi,strVerb,check) )
                            continue
                        infinitive = infi
                        nPersFound = nPersToCheck
                        kTense = numTense
                        bFound = 1
                        break
                        
        # look for peculiar in 3rd (a faire apres les verbes du premier groupe
        # car sinon quand on cherche mangerons, on a le verbe mangaire qui donne aussi mangerons
        if not bFound:
            for infi,tenses in self.aaParticularTrois.items():             
                for numTense,forms in enumerate(tenses):
                    for pers in range(1,7):
                        if nPers != -1 and pers != nPers:
                            continue
                        term = forms[pers-1]
                        end = strVerb[-len(term):]
                        if bVerbose: print("DBG: findInf: aaParticularTrois: comparing %s and %s" % (end,term) )
                        if end == term:
                            infitest = strVerb[:-len(term)]+infi
                            if bVerbose: print("conjugaison found peculiar:" + self.conjugate(infitest,pers,numTense+kTenseFirst))
                            return infitest,pers,numTense+kTenseFirst
                            
        if kTense != kTenseUnknown:
            kTense+=kTenseFirst
        return infinitive, nPersFound,kTense
        
    def printAllConjugaison(self,verb, strComplement=""):
        print("*** Conjugaison du verbe %s ***" % verb)
        for tense in range(kTenseFirst,kTenseMax):
            print("%s:" % tenseToStr(tense))
            for i,subject in enumerate(self.aSubject):
                print("    " + self.conjugate(verb,i+1,tense) + strComplement)
            print("")
        
# class Conjugator - end

        
        
conjugator = Conjugator()
conjugator.load()

def autotest():
    conjugator.load()
    
    # 1er groupe
    assert_equal(conjugator.detectGroup("aimer"),1)
    assert_equal(conjugator.conjugate("aimer"),"j'aime")
    assert_equal(conjugator.conjugate("manger", 2),"tu manges")
    assert_equal(conjugator.conjugate("manger", 4,kTenseFuture),"nous mangerons")
    assert_equal(conjugator.conjugate("manger", 5,kTenseFuture),"vous mangerez")
    assert_equal(conjugator.conjugate("manger", 1,kTenseImperfect),"je mangeais")
    assert_equal(conjugator.conjugate("manger", 1,kTensePast),"je mangeai")
    assert_equal(conjugator.conjugate("aimer", 1,kTensePast),"j'aimai")
    assert_equal(conjugator.conjugate("aimer", 5,kTensePast),"vous aim�tes")
    assert_equal(conjugator.conjugate("manger", 5,kTensePast),"vous mange�tes")
    assert_equal(conjugator.conjugate("manger", 6,kTensePast),"ils mang�rent")
    
    assert_equal(conjugator.findInf("manges"),("manger",2,kTensePresent))
    assert_equal(conjugator.findInf("mange"),("manger",1,kTensePresent))
    assert_equal(conjugator.findInf("mange",3),("manger",3,kTensePresent))
    assert_equal(conjugator.findInf("aiment"),("aimer",6,kTensePresent))
    assert_equal(conjugator.findInf("mange�tes"),("manger",5,kTensePast))
    assert_equal(conjugator.findInf("mangerons"),("manger",4,kTenseFuture)) # ne fonctionne pas: verbe mangerer !?!
    assert_equal(conjugator.findInf("porterons"),("porter",4,kTenseFuture)) # ne fonctionne pas: verbe porterer !?!
    
    # 2ieme groupe
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
    assert_equal(conjugator.conjugate("finir", 5,kTensePast),"vous fin�tes")
    assert_equal(conjugator.conjugate("finir", 6,kTensePast),"ils finirent")
    
    # 3ieme groupe
    assert_equal(conjugator.detectGroup("prendre"),3)
    assert_equal(conjugator.detectGroup("croire"),3)
    assert_equal(conjugator.detectGroup("croitre"),3)
    assert_equal(conjugator.detectGroup("cro�tre"),3)
    assert_equal(conjugator.detectGroup("croitre"),3)
    assert_equal(conjugator.detectGroup("�tre"),3)
    assert_equal(conjugator.detectGroup("avoir"),3)
    assert_equal(conjugator.detectGroup("faire"),3)
    
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
    assert_equal(conjugator.conjugate("croire", 5,kTensePast),"vous cr�tes")
    assert_equal(conjugator.conjugate("croire", 6,kTensePast),"ils crurent")
    
    # compliqu�:
    assert_equal(conjugator.conjugate("cro�tre"),"je cro�s")
    assert_equal(conjugator.conjugate("cro�tre", 1,kTenseFuture),"je cro�trai")
    assert_equal(conjugator.conjugate("cro�tre", 1,kTensePast),"je cr�s")
    assert_equal(conjugator.conjugate("cro�tre", 1,kTenseImperfect),"je croissais")
    
    
    assert_equal(conjugator.conjugate("faire"),"je fais")
    assert_equal(conjugator.conjugate("faire", 2),"tu fais")
    assert_equal(conjugator.conjugate("faire", 3),"il fait")
    assert_equal(conjugator.conjugate("faire", 4),"nous faisons")
    assert_equal(conjugator.conjugate("faire", 5),"vous faites")
    assert_equal(conjugator.conjugate("faire", 6),"ils font")
    assert_equal(conjugator.conjugate("faire", 1,kTenseFuture),"je ferai")
    assert_equal(conjugator.conjugate("faire", 1,kTensePast),"je fis")
    assert_equal(conjugator.conjugate("faire", 1,kTenseImperfect),"je faisais")
    assert_equal(conjugator.conjugate("faire", 4,kTenseFuture),"nous ferons")
    assert_equal(conjugator.conjugate("faire", 4,kTensePast),"nous f�mes")
    assert_equal(conjugator.conjugate("faire", 4,kTenseImperfect),"nous faisions")
    
    
    assert_equal(conjugator.conjugate("�tre"),"je suis")
    assert_equal(conjugator.conjugate("�tre", 2),"tu es")
    assert_equal(conjugator.conjugate("�tre", 3),"il est")
    assert_equal(conjugator.conjugate("�tre", 4),"nous sommes")
    assert_equal(conjugator.conjugate("�tre", 5),"vous �tes")
    assert_equal(conjugator.conjugate("�tre", 6),"ils sont")
    assert_equal(conjugator.conjugate("�tre", 1,kTenseFuture),"je serai")
    assert_equal(conjugator.conjugate("�tre", 1,kTensePast),"je fus")
    assert_equal(conjugator.conjugate("�tre", 1,kTenseImperfect),"j'�tais")
    
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
    assert_equal(conjugator.conjugate("avoir", 4,kTensePast),"nous e�mes")
    assert_equal(conjugator.conjugate("avoir", 4,kTenseImperfect),"nous avions")
    
    print("")
    conjugator.printAllConjugaison("aimer")
    conjugator.printAllConjugaison("manger")
    conjugator.printAllConjugaison("finir")
    conjugator.printAllConjugaison("prendre")
    conjugator.printAllConjugaison("croire")
    conjugator.printAllConjugaison("cro�tre")
    conjugator.printAllConjugaison("d�faire")
    conjugator.printAllConjugaison("symboliser")

    conjugator.printAllConjugaison("�tre")
    conjugator.printAllConjugaison("avoir")
    
    assert_equal(conjugator.findInf("suis"),("�tre",1,kTensePresent))
    assert_equal(conjugator.findInf("sommes"),("�tre",4,kTensePresent))
    assert_equal(conjugator.findInf("aurai"),("avoir",1,kTenseFuture))
    assert_equal(conjugator.findInf("f�mes"),("faire",4,kTensePast))
    assert_equal(conjugator.findInf("finirez"),("finir",5,kTenseFuture))
    assert_equal(conjugator.findInf("prendrai"),("prendre",1,kTenseFuture))
    assert_equal(conjugator.findInf("croyiez"),("croire",5,kTenseImperfect))
    assert_equal(conjugator.findInf("imposibilisator"),("",0,kTenseUnknown))
    
    
    bHaveFun = 0
    if bHaveFun:    
        conjugator.printAllConjugaison("spaghettiser")
        conjugator.printAllConjugaison("ga�attiser")
        conjugator.printAllConjugaison("ga�a")
        conjugator.printAllConjugaison("corto")
        conjugator.printAllConjugaison("alexandre")
        conjugator.printAllConjugaison("elsa")
        conjugator.printAllConjugaison("carvalho")
        conjugator.printAllConjugaison("carvalho", " elsa")
        conjugator.printAllConjugaison("mazel")
        conjugator.printAllConjugaison("lounis")
        conjugator.printAllConjugaison("boufraine")
        conjugator.printAllConjugaison("minecraft")
        conjugator.printAllConjugaison("�cran")
        conjugator.printAllConjugaison("regarder", " l'�cran")
    
if __name__ == "__main__":
    autotest()