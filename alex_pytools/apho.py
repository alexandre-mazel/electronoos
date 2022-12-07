# -*- coding: cp1252 -*-

import io
import os
import sys
import time

import misctools
import stringtools


class Apho:
    def __init__( self ):
        self.thous = [] # list of pair (sentence, author)
        self.aCountSaid = [] # for each sentence, number of said time
        self.aLastSaid = [] # time of last said
        
    def load( self ):
        """
        Charge les pensees: un fichier avec des pensées, puis sur la derniere ligne l'auteur. séparé par des lignes vides.
        eg:
    Je ne pense pas à toute la misère, je pense à la beauté qui reste.
Anne Frank

Fais de ta vie un rêve et d’un rêve une réalité.
Antoine de Saint-Exupery
        """
        f = io.open(misctools.getThisFilePath()+"datas/pensee.txt","r",encoding='cp1252')
        blob = [] # un bloc de ligne de texte séparé par une ligne vide
        while 1:
            line = f.readline()
            if len(line)<1:
                break
            if line[-1] == '\n': line = line[:-1]
            if len(line)<1:
                # end of blob
                if len(blob)>1:
                    citation = " ".join(blob[:-1])
                    auth = blob[-1]
                    self.thous.append( (citation,auth) )
                    self.aCountSaid.append(0)
                    self.aLastSaid.append(0)
                blob = []
            else:
                blob.append(line)
        #~ print(self.thous)
        
    def getThoughts( self, sentence ):
        """
        find a thoughts not said a lot, relative to sentence.
        return a pair, (thought,author) or None if none
        """
        bVerbose = 1
        bVerbose = 0
        
        sentence = sentence.replace('.', ' ').replace(',', ' ')
        words = sentence.split()
        words = stringtools.lowerList(words)
        # add also words without '
        i = 0
        while i < len(words):
            if "'" in words[i]:
                words.extend(words[i].split("'"))
            i += 1
        if bVerbose: print("DBG: getThoughts: words: %s" % words)
        
        # find radical style
        i = 0
        while i < len(words):
            if len(words[i])<4:
                del words[i]
                continue
            # on le fera plus tard pour essayer de matcher sur le mot reel
            #~ if len(words[i])>5:
                #~ words[i] = words[i][:-3] # travailler => travail
            i += 1
            
        match = []
        for t in self.thous:
            cit = t[0]
            cit = cit.lower()
            n = 0
            for w in words:
                if w in cit:
                    if bVerbose or 0: print( "match: '%s' in '%s'" % (w,cit) )
                    #~ n += 1
                    n += len(w) # count more point if word is long!
                if len(w)>5:
                    ws = w[:-3]
                    if ws in cit:
                        if bVerbose: print( "match short: '%s' in '%s'" % (ws,cit) )
                        n += len(ws)
                    
            match.append(n)
        #~ print("match: %s" % match)
        #~ [x for _, x in sorted(zip(Y, X))]
        # both are working, but second seems faster, todolater: measures
        #~ index_order = [x for _, x in sorted(zip(match, range(len(match))),reverse=True)]
        index_order = sorted(range(len(match)), key=lambda k: match[k],reverse=True)
        #~ print("index_order: %s" % index_order)
        # etais ce vraiment la peine de les trier, alors qu'on va les parcourir ensuite ?
        less_said_idx = index_order[0]
        for idx in index_order[1:]:
            if match[idx]<1:
                break
            if time.time()-self.aLastSaid[idx]<5*60:
                continue
            if self.aCountSaid[less_said_idx] > self.aCountSaid[idx]:
                less_said_idx = idx
        print("less_said_idx: %d" % less_said_idx )
        
        if match[less_said_idx] < 1:
            return None
            
        if self.aCountSaid[less_said_idx] > 0 and 0:
            # decide to say already said or not ?
            return None
            
        # first sentence of the list can be selected by default
        if time.time()-self.aLastSaid[less_said_idx]<5*60:
            return None
        
        self.aCountSaid[less_said_idx] += 1
        self.aLastSaid[less_said_idx] = time.time()
        return self.thous[less_said_idx]
        
# class Apho - end

apho = Apho()
apho.load()

global_tts = None
def say(txt):
    global global_tts
    if global_tts == None:
        import pyttsx3
        global_tts = pyttsx3.init()
    if 1:
        txt = txt.replace("Gaia", "Gaya") # le i trema ne passe pas sur le robot
    print("INF: say: '%s'" % txt)
    global_tts.say(txt)
    global_tts.runAndWait()
    
def wordsCallback(words,confidence):
    if confidence<0.6:
        return
    if len(words)<4:
        return
    print("INF: heard: '%s'" % words)
    #~ say(phrase)
    ret = apho.getThoughts(words)
    if ret != None:
        say(ret[0])
        say(ret[1])
        
def test_loop_asr():

    if 0:
        from pocketsphinx import LiveSpeech, get_model_path
        import os
        model_path = get_model_path()
        print("model_path: %s" % model_path )
        # good model path:
        model_path = "C:\\Python39\\Lib\\site-packages\\speech_recognition\\pocketsphinx-data\\"
        strAnsiLang = "fr-FR"
        for phrase in LiveSpeech(
            hmm=(os.path.join(model_path, strAnsiLang)+"\\acoustic-model\\"),
            lm=os.path.join(model_path, strAnsiLang+'\\language-model.lm.bin'),
            dic=os.path.join(model_path, strAnsiLang+'\\pronounciation-dictionary.dict')
        ):
            phrase = str(phrase)
            wordsCallback( phrase, 0.5)

    else:
        # my own one
        import microphone
        microphone.loopProcess(wordsCallback)
            
    
    
    
def autoTest():
    print(apho.getThoughts("j'aime pas travailler"))
    print(apho.getThoughts("j'aime pas travailler"))
    print(apho.getThoughts("j'aime pas travailler"))
    print(apho.getThoughts("j'aime pas travailler"))
    print("")
    #~ print(apho.getThoughts("j'ai la volonté de t'aider"))
    #~ print(apho.getThoughts("j'ai la volonté de t'aider"))
    #~ print(apho.getThoughts("j'ai la volonté de t'aider"))
    #~ print(apho.getThoughts("j'ai la volonté de t'aider"))
    #~ print(apho.getThoughts("j'ai la volonté de t'aider"))
    print("")
    print(apho.getThoughts("Il me faudrait du courage"))
    print(apho.getThoughts("Il me faudrait du courage"))
    print(apho.getThoughts("J'aime le ChamPagne."))
    print(apho.getThoughts("J'aime le vin."))
    print(apho.getThoughts("d'attendre la pluie"))
    if 0:
        # test sur python 2.7
        print(stringtools.accentToHtml("un élève"))
        for i,a in enumerate(apho.thous):
            print(i)
            #~ print(stringtools.accentToHtml(a[0]))
            s1 = stringtools.cp1252ToHtml(a[0])
            s2 = stringtools.cp1252ToHtml(a[1])
            print(s1)
            print(s2)
            print(stringtools.transformAccentToUtf8(a[0]))
            print(stringtools.transformAccentToUtf8(a[1]))
            #~ if i>80:
                #~ break
        
    
if __name__ == "__main__":
    autoTest()
#~ test_loop_asr()