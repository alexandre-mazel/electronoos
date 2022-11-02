# -*- coding: cp1252 -*-
import os
import pocketsphinx
import speech_recognition
import time

# install fr
"""
you have to rename and restructure the files in the language zip folder:

etc/voxforge_it_sphinx.lm > speech_recognition/pocketsphinx-data/fr-FR/language-model.lm.bin
etc/voxforge_it_sphinx.dic > speech_recognition/pocketsphinx-data/fr-FR/pronounciation-dictionary.dict
model_parameters/voxforge_it_sphinx.cd_cont_2000/ > speech_recognition/pocketsphinx-data/fr-FR/acoustic-model/

in C:\Python39\Lib\site-packages\speech_recognition\pocketsphinx-data\fr-FR

download from:
https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French/
=> 4s sur mon exemple de sieste2 (mstab7)
or from:
https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst
=> 1s sur mon exemple de sieste2 (mstab7)
"""


strSoundFilename = "C:/tmp/sieste.wav"
strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/la_sieste2.wav" # => il envie de faire la sieste
#~ strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/pepper_ecoute_moi.wav" # => et leurs écoute moi
#~ strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/au_secours.wav" # => au secours
strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/aime_tu_les_haricots_verts.wav" # => julia et pauvert
#~ strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/je_suis_bien_content.wav" # =>  je suis bien contents
#~ strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/a_table.wav" # =>  atteint le
strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/pepper.wav" # =>  dépasse
strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/ecoute_moi.wav" # =>  je moi
strAnsiLang = "fr-FR"

if 0:
    # en
    strSoundFilename = "C:/Users/alexa/dev/git/electronoos/cherie/test_brice.wav"
    strAnsiLang = "en-US"
    
    

if 0:
    from pocketsphinx import LiveSpeech
    for phrase in LiveSpeech(): # language = strAnsiLang
        print(phrase)
    
import sys
sys.path.append("../alex_pytools/")
import sound_player
if 0:
    # play it:
    sound_player.soundPlayer.playFile(strSoundFilename,bWaitEnd=1)
    
keyword_entries = None
if 0:
    # list of keyword with sensitivity
    # where ``keyword`` is a phrase, and ``sensitivity`` is how sensitive to this phrase the recognizer should be, on a scale of 0 (very insensitive, more false negatives) to 1 (very sensitive, more false positives
    # je n'ai rien trouvé qui marche aussi bien que du freespeech (juste ca met 0.5s au lieu de 1s)
    keyword_entries = [
        ("J'ai envie de faire la sieste", 0.1),
        ("au secours",0.1),
    ]
    
    keyword_entries = [("sieste",0.9),("au secours",0.1)]
    keyword_entries = [("faire",0.9),("sieste",0.5),("au secours",0.5)]
    
    if 1:
        rSensi = 0.5
        keyword_entries = [
            ("j'ai",rSensi),("envie",rSensi),("de faire",rSensi),("la sieste",rSensi),
            ("pepper",rSensi),("pepper écoute moi",rSensi),("au secours",rSensi),("secours",rSensi),
            ("aime",rSensi),("haricots",rSensi),("verts",rSensi),
        ]

r = speech_recognition.Recognizer()
#~ print(dir(r))

def recognizeFromFile(filename,language = "en-US"):
    """
    return recognised_sentence,score,proba
    """
    bVerbose=0
    retVal = None

    with speech_recognition.WavFile(filename) as source:
        audio = r.record(source) # read the entire WAV file
    # recognize speech using  Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        timeBegin = time.time()
        bShowAll = 0
        bShowAll = 1
        retFromReco =r.recognize_sphinx(audio, language = strAnsiLang, keyword_entries=keyword_entries, show_all = bShowAll )
        if bVerbose: print("Duration: %.3fs" % (time.time()-timeBegin))
        if bVerbose: print( "retFromReco: %s" % str(retFromReco) )
        
        if bShowAll:
            if bVerbose: print( "retFromReco: dir %s" % str(dir(retFromReco.hyp()) ))
            if bVerbose: print( "retFromReco3: prob: %s" % str(retFromReco.hyp().prob ) )
            if bVerbose: print( "retFromReco3: score: %s" % str(retFromReco.hyp().score ) )
            if bVerbose: print( "retFromReco3: best_score: %s" % str(retFromReco.hyp().best_score ) )
            if bVerbose: print( "retFromReco3: hypstr: %s" % str(retFromReco.hyp().hypstr ) )
            
            if retFromReco != None and retFromReco.hyp() != None:
                retVal = retFromReco.hyp().hypstr,retFromReco.hyp().best_score,retFromReco.hyp().prob
            
            """
            A propos de la confidence:

        Confidence result is not returned by the current version of speech-recognition. If you look at the implementation:

    def recognize_sphinx(...):
       ...
       # return results
       hypothesis = decoder.hyp()
       if hypothesis is not None: return hypothesis.hypstr
       raise UnknownValueError()  # no transcriptions available

    what about overloading the recognize_sphinx method in your project: 
    you define your own flavour of the method then you do a r.recognize_sphinx = my_own_private_method() 

            """
            
        if retFromReco != [] and 0:
            
            alt = retFromReco['alternative']
            strTxt = alt[0]['transcript']

            # when reco does not return a confidence, use -1 as an error code
            if 'confidence' in alt[0]:
                rConf = alt[0]['confidence']
            else:
                log.debug('no confidence returned')
                rConf = -1.0
        
            #~ strTxt = self.cleanText2( strTxt )
            print("Speech Recognition thinks you said: '%s' (conf:%5.2f)\n" % (strTxt, rConf) )
            retVal = [ [strTxt,rConf] ]
        

    except speech_recognition.UnknownValueError:
        pass
        
    except speech_recognition.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
        
    if retVal == None: 
        if bVerbose: print("Speech Recognition could not understand audio\n")

    if bVerbose: print("DBG: retVal: %s" % str(retVal) )
    return retVal
    
global_tts = None
def say(txt):
    global global_tts
    if global_tts == None:
        import pyttsx3
        global_tts = pyttsx3.init()
    global_tts.say(txt)
    global_tts.runAndWait()
        
def recognizeFromFolder(strPath):
    bUseTts = 1
        
    strAnsiLang = "fr-FR"
    listFiles = os.listdir(strPath)
    listFiles = sorted(listFiles)

    #~ if bUseTts: say("coucou")

        
    for f in listFiles:
        strSoundFilename = strPath+f
        sound_player.soundPlayer.playFile(strSoundFilename,bWaitEnd=0)
        
        if 0:
            # just play them in a raw
            print(f)
            sound_player.soundPlayer.waitAll()
            continue
        
        recognized = recognizeFromFile(strSoundFilename,strAnsiLang)
        print("%s: %s" % (f,recognized))
        
        sound_player.soundPlayer.waitAll() # attend de finir le son pour lire le suivant
        if recognized != None:
            if bUseTts: say(recognized[0])
        
#~ recognizeFromFile( strSoundFilename, strAnsiLang )
strPath = "D:/cherie_sound_classified/bruit/"
strPath = "D:/cherie_sound_classified/voix/"
recognizeFromFolder(strPath)
