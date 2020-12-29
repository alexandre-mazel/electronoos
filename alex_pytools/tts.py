# -*- coding: utf-8 -*-
"""
tts du pauvre v2
"""
import wav
import misctools
import pygame_tools


import os
import time


#~ print( levenshtein( "bateau", "batau" ) );
#~ print( levenshtein( "bateau", "bataux" ) );
#~ print( levenshtein( "KSTLPRSTNTTSTTSNS", "KSTPRKPM" ) );

def isPhoneticEqual( s1, s2 ):
    """
    return the phonetic equality between of two string: [0., .. 1.] : 0 completely different, from 0 to 1: the more ressembling, 1: equal]
    """
    import metaphone
    #~ print metaphone.dm( unicode(s1) )
    #~ print metaphone.dm( unicode(s2) )
    try:
        meta1 = metaphone.dm( unicode(s1) )[0]
        meta2 = metaphone.dm( unicode(s2) )[0]
    except BaseException, err:
        print( "ERR: can't metaphone '%s' or '%s': err: %s" % (s1, s2, err ) )
        meta1 = s1
        meta2 = s2
    if meta1 == meta2:
        return 1.

    rMidLen = ( len(meta1) + len( meta2 ) ) / 2;
    if( rMidLen < 1 ):
        return 0.
    rDist = 0.9 - levenshtein( meta1, meta2 )/float(rMidLen)
    if( rDist < 0. ):
        rDist = 0.
    return rDist
# isPhoneticEqual - end



class Tts:
    
    def __init__( self ):
        self.dWord = dict() # for each word, a list of wavfile
        
        
    def load( self, strPath ):
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
        
        
        
    def sayToFile( self, txt ):
        """
        generate a wavfile and save it.
        return the filename
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
            for sentence in listSentences:
                words = nltk.tokenize.word_tokenize(sentence)
                print("words: %s" % words)
                idxend = len(words)
                while len(words) > 0:
                    if words[0] in [ "," , ";", "!", "?", ".", ":" ]:
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
                    tomatch = "_".join(words[:idxend]).lower()
                    #~ print("tomatch: %s" % tomatch)
                    for k,f in self.dWord.items():
                        if k == tomatch:
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
                
            
            
        wav.concatenateWav(listSound, strOutputFilename, 0.1)
        return strOutputFilename
        
    def say( self, txt ):
        wavfile = self.sayToFile(txt)
        misctools.playWav(wavfile)
        
        
        
        
# class Tts - end
        
tts = Tts()

def autoTest():
    tts = Tts()
    tts.load("c:/tts_alexandre/")
    #~ tts.say("je aimer toi")
    #~ tts.say("je aimer toi, toi aimer moi.")
    tts.say("Je aimer toi, toi aimer moi. Moi gentil.")
    #~ tts.say("c'est la phrase dites initialement par Tarzan.")
    #~ tts.say("je etre gentil, et toi? Moi ca va !") # manque etre et avoir !!!
    #~ tts.say("toi faim?")
    
    
if __name__ == "__main__":
    autoTest()