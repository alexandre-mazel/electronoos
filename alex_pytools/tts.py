# -*- coding: utf-8 -*-
"""
tts du pauvre v2
"""
import wav
import misctools
import pygame_tools


import os
import time


class Tts:
    
    def __init__( self ):
        self.dWord = dict() # for each word, a list of wavfile
        
        
    def load( self, strPath = None ):
        if strPath == None:
            strPath = misctools.getUserHome() + "tts_alexandre/"
        self.strPath = strPath
        for f in sorted(  os.listdir(strPath) ):
            words = f.split(".")[0].split("__")
            if len(words)>1:
                strWord = words[-1]
                if strWord not in self.dWord.keys():
                    self.dWord[strWord] = []
                self.dWord[strWord].append(f)
                #~ print("INF: '%s' => '%s'" % (strWord, self.dWord[strWord] ) )
            else:
                print("WRN: '%s' no keyword found" % f )
        print("INF: load finished")
        
        
        
    def sayToFile( self, txt ):
        """
        generate a wavfile and save it.
        return filename,rSpeechDuration
        """
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
                        print("txt found: %s" % k )
                        print("txt remaining: %s" % txt )
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
            print("listSentences: %s" % listSentences)
            separators = [ "," , ";", "!", "?", ".", ":" ]
            for sentence in listSentences:
                words = nltk.tokenize.word_tokenize(sentence)
                print("words: %s" % words)
                idxend = len(words)
                while len(words) > 0:
                    if words[0] in separators :
                        if words[0] in [ "," , ";", ":"]:
                            # insert silence 
                            for i in range(1):
                                listSound.append(self.strPath+"silence_100ms.wav")
                                
                        if words[0] in [ ".", "!", "?"]:
                            # insert silence 
                            for i in range(2):
                                listSound.append(self.strPath+"silence_100ms.wav")
                                
                        words = words[1:]
                        continue
                    if idxend > 1:
                        if words[idxend-1] in separators:
                            tomatch = "_".join(words[:idxend-1]).lower()
                        else:
                            tomatch = "_".join(words[:idxend]).lower()
                    else:
                        tomatch = words[0].lower()
                    #~ print("tomatch: %s" % tomatch)
                    for k,f in self.dWord.items():
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
                                print("INF: sayToFile: word not found: %s" % words[:idxend] )
                                words = words[1:]
                                idxend = len(words)
                            else:
                                idxend -= 1
                
            
            
        if len(listSound) > 1:
            rDuration = wav.concatenateWav(listSound, strOutputFilename, 0.1)
        else:
            print("WRN:tts.sayToFile: nothing to say for '%s'" % txt )
            strOutputFilename = self.strPath+"silence_100ms.wav"
            rDuration = 0.1
        return strOutputFilename, rDuration
        
    def say( self, txt ):
        wavfile,rDuration = self.sayToFile(txt)
        misctools.playWav(wavfile)
        
        
    def manque( self ):
        """
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
        
tts = Tts()

def autoTest():
    tts = Tts()
    tts.load()
    #~ tts.say("je aimer toi")
    #~ tts.say("je aimer toi, toi aimer moi.")
    #~ tts.say("Je aimer toi, toi aimer moi. Moi gentil.")
    tts.say("toi vouloir manger chocolat puis medicament?")
    #~ tts.say("c'est la phrase dites initialement par Tarzan.")
    #~ tts.say("je etre gentil, et toi? Moi ca va !") # manque etre et avoir !!!
    #~ tts.say("toi faim?")
    
    tts.say("ok")
    
    
if __name__ == "__main__":
    autoTest()