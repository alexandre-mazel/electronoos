# -*- coding: utf-8 -*-
"""
tts du pauvre v2
"""
import wav
import misctools
import pygame_tools


import os
import time

#~ def tts_google():
# cf tts_say
    


class Tts:
    
    def __init__( self ):
        self.dWord = dict() # for each word, a list of wavfile
        self.bLoaded = False
        
    def isLoaded( self ):
        return self.bLoaded
        
    def getInfinitif( self, word ):
        if word == "mangent":
            return "manger"
        
        if word == "suis" or word == "est":
            return "etre"
            
        if "ajout" in word:
            return "ajouter"

        if "fait" in word:
            return "faire"
            
        # TODO: la vraie methode!
        
        return "not found"
        
        
    def load( self, strPath = None ):
        if self.bLoaded: return
        if strPath == None:
            strPath = misctools.getUserHome() + "tts_alexandre/"
        self.strPath = strPath
        for f in sorted(  os.listdir(strPath) ):
            if not os.path.isfile(strPath+f):
                continue
            if not ".wav" in f:
                continue
            words = f.split(".")[0].split("__")
            if len(words)>1:
                strWord = words[-1]
                if strWord not in self.dWord.keys():
                    self.dWord[strWord] = []
                self.dWord[strWord].append(f)
                #~ print("INF: '%s' => '%s'" % (strWord, self.dWord[strWord] ) )
            else:
                print("WRN: '%s' no keyword found in this name" % f )
        self.bLoaded = True
        print("INF: load finished")
        
        
        
    def sayToFile( self, txt ):
        """
        generate a wavfile and save it.
        return filename,rSpeechDuration
        """
        
        # BEURK: code trop gros avec trop de niveau de boucles
        bDebug = 0
        if bDebug: print("\n\nDBG: sayToFile('%s') - begin" % txt )
        data = misctools.cache.get("tts_saytofile_" + txt )
        if data != False:
            f,r = data
            return f,r
        strOutputFilename = misctools.getTempFilename() + ".wav"
        listSound = []
        
        if 0:
            # dumb letter par letter
            txt = txt.strip(" !?,;")
            idxend = len(txt)
            while len(txt) > 0:
                for k,f in self.dWord.items():
                    if k == txt[:idxend]:
                        listSound.append(self.strPath+f[0])
                        txt = txt[idxend:].strip()
                        if bDebug: print("txt found: %s" % k )
                        if bDebug: print("txt remaining: %s" % txt )
                        idxend = len(txt)
                        break
                else:
                    print("INF: sayToFile: cannot match: %s" % txt[:idxend] )
                    idxend -= 1
                    if idxend == -1:
                        break
        else:
            import nltk
            #~ words = txt.split(",.;?!") # split works only with one separator
            #~ print("words: %s" % words)
            listSentences = nltk.tokenize.sent_tokenize(txt)
            if bDebug: print("listSentences: %s" % listSentences)
            separators = [ "," , ";", "!", "?", ".", ":" ]
            for sentence in listSentences:
                words = nltk.tokenize.word_tokenize(sentence)
                if bDebug: print("words: %s" % words)
                idxend = len(words)
                while len(words) > 0:
                    if words[0] in separators :
                        if words[0] in [ "," , ";", ":"]:
                            # insert silence 
                            # ne passe jamais la !
                            for i in range(2):
                                print("DBG: insert silence...")
                                listSound.append(self.strPath+"silence_100ms.wav")
                                
                        if words[0] in [ ".", "!", "?"]:
                            # insert silence 
                            #ni la !
                            for i in range(5):
                                print("DBG: insert silence...")
                                listSound.append(self.strPath+"silence_100ms.wav")
                                
                        words = words[1:]
                        continue
                    if idxend > 1 and len(words)>idxend-1:
                        if words[idxend-1] in separators:
                            tomatch = "_".join(words[:idxend-1]).lower()
                        else:
                            tomatch = "_".join(words[:idxend]).lower()
                    else:
                        tomatch = words[0].lower()
                    #~ print("tomatch: %s" % tomatch)
                    for k,f in self.dWord.items():
                        if bDebug: print("comp: '%s' and '%s'" % (k,tomatch))
                        #~ if k == tomatch:
                        if k == tomatch:
                            listSound.append(self.strPath+f[0])
                            words = words[idxend:]
                            #~ print("words found: %s" % k )
                            #~ print("words remaining: %s" % words )
                            idxend = len(words)
                            break # for
                    else:
                        for k,f in self.dWord.items():
                            rSame = misctools.getPhoneticComparison( k, tomatch)
                            if  rSame > 0.8:
                                print("WRN: using %s instead of %s (rSame=%4.2f)" % (k,tomatch,rSame) )
                                listSound.append(self.strPath+f[0])
                                words = words[idxend:]
                                #~ print("words found: %s" % k )
                                #~ print("words remaining: %s" % words )
                                idxend = len(words)
                                break # for
                        else:
                            if idxend == 1:
                                # word not found
                                infi = self.getInfinitif(words[:idxend][0])
                                for k,f in self.dWord.items():
                                    rSame = misctools.getPhoneticComparison( k, infi )
                                    if rSame > 0.9:
                                        print("WRN: using infinitif for %s => %s (rSame=%4.2f)" % (words[:idxend],infi,rSame) )
                                        listSound.append(self.strPath+f[0])
                                        words = words[idxend:]
                                        #~ print("words found: %s" % k )
                                        #~ print("words remaining: %s" % words )
                                        idxend = len(words)
                                        break # for
                                else:
                                    print("INF: sayToFile: word not found: %s" % words[:idxend] )
                                    words = words[1:]
                                    idxend = len(words)
                            else:
                                idxend -= 1
                
            
            
        if len(listSound) > 0:
            if 1:
                print("DBG: list sound:" )
                for s in listSound:
                    print("DBG:   %s" % s)
            rDuration = wav.concatenateWav(listSound, strOutputFilename, 0.1)
        else:
            print("WRN:tts.sayToFile: nothing to say for '%s'" % txt )
            strOutputFilename = self.strPath+"silence_100ms.wav"
            rDuration = 0.1
            
        misctools.cache.store("tts_saytofile_" + txt, (strOutputFilename, rDuration) )
        return strOutputFilename, rDuration
        
    def say( self, txt ):
        wavfile,rDuration = self.sayToFile(txt)
        misctools.playWav(wavfile)
        
        
    def manque( self ):
        """
        recorded in long_texte_part*
        etre, avoir, vouloir, manger, dormir, lire, jouer, ecouter, faire la sieste, creer, cuisiner, tricoter,
        faire dodo, dormir, calin, caliner, copier, recopier, pleurer, heureux, triste, sauter,
        danser, gouter, dejeuner, diner, souper, petit dejeuner, grand, grosse, fin, maigre,
        luxueux, luxe, grand, petit, rond, carre, triangulaire, rectangle, rectangulaire,
        plein, vide, grenier, cave, salon, salle a manger, chambre, toilette, salle de bains,
        entree, jardin, rue, boulevard, chemin, villa, avenue, champs, elisee, elisa, alexandre,
        patricia, elsa, corto, gaia, nicole, le, la, les, roux, brun, blond, brune, blonde, rousse,
        rousseurs, grains, 
        jeopardy, monopoly, monopole, oie, echec, dame, poker, jeu, belotte, solitaire,
        extraverti, introverti, monotone, anime, calme, silence, poubelle, bruit, oreiller,
        drap, couverture, couette, barette, cheveux, torve, epaule, jambe, pied, orteil,
        doigts, main, hanche, coude, tete, cou, articulation, 
        gras, lipide, glucide, proteine, vitamine, sel, poivre, mineraux, vegetaux, sucre
        loi,
        tres, menteur, menteuse, copine, plus, arreter, m'embeter, arrete,
        stop, super, beau, c'est, genial, boom, trop, nul, chez, viens, top,
        on va faire ca, on va jouer, viens on va regarder, elle est trop belle,
        j'aime, j'aime bien, sa robe, robe, ballon, trop fort, 
        puree, fichtre, flute, superfloute, mille sabord, sacripan, millier,
        milliard, million, une, un, l'infini, a, jamais, toujours, parfois,
        des fois, quelques, fois, quelques fois, bonne nuit, bonjour, salut, hello,
        bonne journee, journee, soiree, matinee, 
        chat, chocolat, la mer, mer, maitresse, maitre, j'aime pas les epinards.
        casser, reparer, quitter, marrier, se, divorcer, perir, mourir, 
        initialement, medicament, puis, source, eau, vin, 
        + imagier LCDL super imagier
        """
        pass
        
        
# class Tts - end

# pour generer des sons, prendre un son avec pleins de mots entouré de blanc et faire:
if 0:
    import sound_processing
    txt = "bonjour_monsieur_madame_.wav"
    txt = "long_texte_part1.wav"
    txt = "long_texte_part2.wav"
    txt = "serie_courte_monsieur.wav"
    txt = "mot_par_occ_111sur1500.wav"
    txt = "pluie_et_beau_temps.wav"
    txt = "phrase_lente.wav"
    sound_processing.autocut("c:/tts_alexandre/rough/"+txt,bAutoRename=1,bAlternativeManualInputted=1)
    exit()
        
tts = Tts()

def autoTest():
    tts = Tts()
    tts.load()
    
    francais_et_petit_dej ="Les Francais ne mangent pas beaucoup au petit-dejeuner. En general, les adultes boivent un bol ou une grande tasse de cafe ou de cafe au lait. Le cafe est assez fort, quand le cafe n’est pas fort, on dit que c’est du 'jus de chaussette'. Souvent on ajoute un peu de sucre."
    #~ tts.say("je aimer toi")
    #~ tts.say("je aimer toi, toi aimer moi.")
    #~ tts.say("Je aimer toi, toi aimer moi. Moi gentil.")
    #~ tts.say("toi vouloir manger chocolat puis medicament?")
    #~ tts.say("Bonjour Monsieur !")
    #~ tts.say("J'aime les haricots et les petits pois")
    #~ tts.say("L'autre jour, j'ai vu un chien, un chat et une pizza. Et toi ?")
    #~ tts.say("c'est la phrase dites initialement par Tarzan.")
    #~ tts.say("je etre gentil, et toi? Moi ca va !") # manque etre et avoir !!!
    #~ tts.say("toi faim?")
    #~ tts.say(francais_et_petit_dej)
    #~ tts.say("c'est le matin, il fait pas chaud aujourd'hui!")
    tts.say("Ho il fait pas chaud aujourd'hui!")
    #~ tts.say("c'est le matin ou le soir, il fait pas chaud aujourd'hui!")  #  ne fonctionne pas: matin ou => matinée
    
    #~ tts.say("moi")
    #~ tts.say("ok")
    #~ tts.say("ok")
    
    
if __name__ == "__main__":
    autoTest()