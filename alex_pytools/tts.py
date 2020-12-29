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
        
        
    def load( self, strPath ):
        self.strPath = strPath
        for f in sorted(  os.listdir(strPath) ):
            strWord = f.split(".")[0].split("__")[-1]
            if strWord != "":
                if strWord not in self.dWord.keys():
                    self.dWord[strWord] = []
                self.dWord[strWord].append(f)
                #~ print("INF: '%s' => '%s'" % (strWord, self.dWord[strWord] ) )
        
        
        
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
                    for k,f in self.dWord.items():
                        if k == "_".words[:idxend]: check ici et finir
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
    tts.say("je etre gentil, et toi? Moi ca va!") # manque etre et avoir !!!
    #~ tts.say("toi faim?")
    
    
if __name__ == "__main__":
    autoTest()