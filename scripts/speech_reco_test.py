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

        timeBegin = time.time()
        bShowAll = 0
        bShowAll = 1
        
        bUseSphinx = 0
        bUseSphinx = 1
        
        if not bUseSphinx:
            #~ import sound_processing
            #~ retFromReco = sound_processing.getSpeechInWav(filename)
            retFromReco = r.recognize_google(audio, language = strAnsiLang, show_all = bShowAll)
            
            if bVerbose: print( "retFromReco: %s" % str(retFromReco) )

        else:
            retFromReco = r.recognize_sphinx(audio, language = strAnsiLang, keyword_entries=keyword_entries, show_all = bShowAll )
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
                
                
        if retFromReco != [] and not bUseSphinx:
            
            alt = retFromReco['alternative']
            strTxt = alt[0]['transcript']

            # when reco does not return a confidence, use -1 as an error code
            if 'confidence' in alt[0]:
                rConf = alt[0]['confidence']
            else:
                log.debug('no confidence returned')
                rConf = -1.0
        
            #~ strTxt = self.cleanText2( strTxt )
            if bVerbose: print("Speech Recognition thinks you said: '%s' (conf:%5.2f)\n" % (strTxt, rConf) )
            retVal = [ strTxt,rConf, 0.5 ]
        

    except speech_recognition.UnknownValueError as e:
        print("ERR: UnknownValueError: err:%s" % str(e) )
        
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
        if "2022_11_02-15h57" not in f and "2022_11_02-15h56" not in f:
            continue
        strSoundFilename = strPath+f
        sound_player.soundPlayer.playFile(strSoundFilename,bWaitEnd=0)
        
        if 0:
            # just play them in a row
            print(f)
            sound_player.soundPlayer.waitAll()
            continue
        
        recognized = recognizeFromFile(strSoundFilename,strAnsiLang)
        print("%s: %s" % (f,recognized))
        
        sound_player.soundPlayer.waitAll() # attend de finir le son pour lire le suivant
        if recognized != None:
            if bUseTts: say(recognized[0])
            
        # if google, add a pause
        time.sleep(1)

def sendInOneBigWav(strPath):
    import wav
        
    strAnsiLang = "fr-FR"
    listFiles = os.listdir(strPath)
    listFiles = sorted(listFiles)

    #~ if bUseTts: say("coucou")

    listWavs = []
    for f in listFiles:
        if "2022_11_02-15h57" not in f and "2022_11_02-15h56" not in f:
            continue
        listWavs.append(strPath+f)
    
    bigsound = "/tmp/big.wav"
    print("INF: concatenating...")
    wav.concatenateWav(listWavs, bigsound,rInsertSilenceBetween=0.1)
    print("INF: recognizing...")
    ret = recognizeFromFile(bigsound,strAnsiLang)
    print(ret)

"""
discussion du psy:
sphinx:
2022_11_02-15h56m07s671758ms_speech.wav: ('ensuite il a pauvert thiberville', 0.26619295873300225, 1.6241381305030788e-07)
2022_11_02-15h56m09s262763ms_speech.wav: ('ce plafond', 0.644694929584918, 0.0005435308262084263)
2022_11_02-15h56m13s362201ms_speech.wav: ('la jolibois services', 0.3298739890870922, 0.0008947653450251868)
2022_11_02-15h56m16s546388ms_speech.wav: ('on voit le succès on voit dans la', 0.326624510523984, 2.3849015980556597e-06)
2022_11_02-15h56m17s456973ms_speech.wav: ('pas vu le', 0.6180561663431007, 7.158515937261324e-05)
2022_11_02-15h56m20s413986ms_speech.wav: ('directeur du petit du métier de base', 0.23644777976520462, 3.803170999575696e-09)
2022_11_02-15h56m23s825862ms_speech.wav: ("c' est aires la devise de joie", 0.27539866937764984, 1.6746035068209907e-10)
2022_11_02-15h56m25s763502ms_speech.wav: ('par le meilleur', 0.7054759792108088, 0.0927468901046429)
2022_11_02-15h56m27s129701ms_speech.wav: ('avec eux', 0.5447819631268591, 0.00046642352457862033)
2022_11_02-15h56m28s945450ms_speech.wav: ('le signe', 0.7361033999773845, 0.04273477166133514)
2022_11_02-15h56m29s855854ms_speech.wav: ('ce livre', 0.720879246655183, 0.0013374784960335528)
2022_11_02-15h56m30s765639ms_speech.wav: ('page trente', 0.6352876970247876, 0.2127744434794177)

2022_11_02-15h56m32s929334ms_speech.wav: ('euh je vais de parler lourds', 0.37626893889286506, 2.725770622157222e-06)
2022_11_02-15h56m33s727486ms_speech.wav: ('', 0.8193122291024348, 0.39520384532027664)
2022_11_02-15h56m36s117807ms_speech.wav: ('mon fils a envoyé un message clair', 0.3766077164262979, 0.0001641443607185544)
2022_11_02-15h56m38s847853ms_speech.wav: ('on disait que sa copie', 0.507800757868099, 0.01534767681558785)
2022_11_02-15h56m39s641064ms_speech.wav: ('li n', 0.6010515666599379, 0.0017438108426325002)
2022_11_02-15h56m40s455566ms_speech.wav: ('le', 0.7350736277139435, 0.03308982067543563)
2022_11_02-15h56m42s160378ms_speech.wav: ('si tu eux-mêmes', 0.6369415113747654, 0.001644729252649323)
2022_11_02-15h56m43s185086ms_speech.wav: ('voiture', 0.5912751951328047, 0.17813497300075284)
2022_11_02-15h56m46s464903ms_speech.wav: ('expliquer', 0.6156505615508935, 1.0)
2022_11_02-15h56m47s380608ms_speech.wav: ("ce n' est pas pour elle", 0.5665037454950821, 2.1476261254910523e-06)
2022_11_02-15h56m48s403373ms_speech.wav: ('la', 0.812134269718998, 0.05241027758190352)
2022_11_02-15h56m52s042329ms_speech.wav: ("ça veut pas dire que euh qui aime pas qui n' est pas", 0.26478593829915054, 7.753156264073306e-11)
2022_11_02-15h56m54s794944ms_speech.wav: ('simplement huit pense pas', 0.47937925179221724, 0.00017901005083949422)
2022_11_02-15h56m57s274666ms_speech.wav: ('là ce qui est fabre', 0.4986428318654437, 1.00803279276272e-05)
2022_11_02-15h56m57s863008ms_speech.wav: ('ferroviaire', 0.7187918294268445, 0.7129221285674296)
2022_11_02-15h56m58s981015ms_speech.wav: ('sur un message au caire', 0.5258875527489131, 0.0022179000695614274)
2022_11_02-15h57m11s514849ms_speech.wav: ("l' enfer", 0.691853133145901, 0.002798403873283195)
2022_11_02-15h57m14s681158ms_speech.wav: ("or j' espère percé", 0.41792370881661517, 0.005329284566712222)
2022_11_02-15h57m15s723150ms_speech.wav: ('et circonspect', 0.641993023947133, 0.054011727788598994)
2022_11_02-15h57m17s526408ms_speech.wav: ('qui ne sachant pas très bien', 0.5052176955613222, 0.0008031704028435638)
2022_11_02-15h57m18s454488ms_speech.wav: ('le tigre', 0.7109288381790609, 0.03760057388006218)
2022_11_02-15h57m22s889359ms_speech.wav: ('et gardé ce message', 0.5114699330496703, 0.026587379329326973)
2022_11_02-15h57m25s833486ms_speech.wav: ('et réfléchir à ce poste du', 0.3761184689366778, 1.681313147187098e-05)
2022_11_02-15h57m27s995749ms_speech.wav: ('ce jeudi', 0.642442553904903, 0.018969900157731354)
2022_11_02-15h57m29s373289ms_speech.wav: ('la foi', 0.5695709864588457, 0.11457889233534206)
2022_11_02-15h57m30s612449ms_speech.wav: ('', 0.7768660200571209, 0.3460586728682183)
2022_11_02-15h57m33s567640ms_speech.wav: ("voilà j' ai fait", 0.6597599604611475, 0.00116508380664762)

2022_11_02-15h57m44s734020ms_speech.wav: ("l' équipement", 0.7094375286062014, 0.69720069659662)
2022_11_02-15h57m46s309770ms_speech.wav: ('cela', 0.7524762976852312, 0.019578889919276244)

google:
2022_11_02-15h56m07s671758ms_speech.wav: ["ensuite y a point vert j'ai vu un visage", 0.86659491, 0.5]
2022_11_02-15h56m09s262763ms_speech.wav: None
2022_11_02-15h56m13s362201ms_speech.wav: None
2022_11_02-15h56m16s546388ms_speech.wav: None
2022_11_02-15h56m17s456973ms_speech.wav: None
2022_11_02-15h56m20s413986ms_speech.wav: None
2022_11_02-15h56m23s825862ms_speech.wav: ["c'est bon tu as", 0.76424927, 0.5]
2022_11_02-15h56m25s763502ms_speech.wav: None
2022_11_02-15h56m27s129701ms_speech.wav: None
2022_11_02-15h56m28s945450ms_speech.wav: None
2022_11_02-15h56m29s855854ms_speech.wav: None
2022_11_02-15h56m30s765639ms_speech.wav: None

2022_11_02-15h56m32s929334ms_speech.wav: ['je vais te parler de mon fils', 0.93855578, 0.5]
2022_11_02-15h56m33s727486ms_speech.wav: None
2022_11_02-15h56m36s117807ms_speech.wav: ["mon fils m'a envoyé un message", 0.93855578, 0.5]
2022_11_02-15h56m38s847853ms_speech.wav: ['je me disais que ça coupe', 0.85242361, 0.5]
2022_11_02-15h56m39s641064ms_speech.wav: None
2022_11_02-15h56m40s455566ms_speech.wav: None
2022_11_02-15h56m42s160378ms_speech.wav: ["si tu m'aimes", 0.9385559, 0.5]
2022_11_02-15h56m43s185086ms_speech.wav: ["pourquoi tu m'appelles", 0.91752917, 0.5]
2022_11_02-15h56m46s464903ms_speech.wav: ['expliquer', 0.68295991, 0.5]
2022_11_02-15h56m47s380608ms_speech.wav: None
2022_11_02-15h56m48s403373ms_speech.wav: None
2022_11_02-15h56m52s042329ms_speech.wav: ["ça veut pas dire que qu'il aime pas qui mais", 0.86744374, 0.5]
2022_11_02-15h56m54s794944ms_speech.wav: ["simplement il n'y pense pas", 0.93855584, 0.5]
2022_11_02-15h56m57s274666ms_speech.wav: ["il m'a raconté ça", 0.93855584, 0.5]
2022_11_02-15h56m57s863008ms_speech.wav: None
2022_11_02-15h56m58s981015ms_speech.wav: ['message', 0.93855584, 0.5]
2022_11_02-15h57m11s514849ms_speech.wav: None
2022_11_02-15h57m14s681158ms_speech.wav: ['je suis resté assez', 0.90096891, 0.5]
2022_11_02-15h57m15s723150ms_speech.wav: ['circonspect', 0.93855584, 0.5]
2022_11_02-15h57m17s526408ms_speech.wav: ['ne sachant pas très', 0.87957847, 0.5]
2022_11_02-15h57m18s454488ms_speech.wav: None
2022_11_02-15h57m22s889359ms_speech.wav: ["j'ai gardé ce message", 0.93855584, 0.5]
2022_11_02-15h57m25s833486ms_speech.wav: ['je vais réfléchir à ce que je vais aller', 0.92572242, 0.5]
2022_11_02-15h57m27s995749ms_speech.wav: None
2022_11_02-15h57m29s373289ms_speech.wav: ['plein de fois', 0.91309446, 0.5]
2022_11_02-15h57m30s612449ms_speech.wav: None
2022_11_02-15h57m33s567640ms_speech.wav: ["voilà j'ai fini", 0.9385559, 0.5]

in one big:
["ensuite y a point vert j'ai vu un visage aucun visage ça le problème tu vois il marche bien c'est bon donc 
je vais te parler de mon fils
mon fils m'a envoyé un message hier me disait que sa copine me disais la même 
si tu m'aimes pourquoi tu m'appelles pas m'expliquer qui comprenait pas pourquoi il peut pas que ça veut pas dire que qu'il aime pas qu'il m'aime pas 
simplement il n'y pense pas il m'a raconté ça pendant plusieurs minutes sur un message pour donc je suis resté assez circonspect 
ne sachant pas très bien quoi dire j'ai gardé ce message 
je vais réfléchir à ce que je vais lui dire qu'elle j'ai déjà eu plein de fois 
voilà j'ai fini
tu me demandes tout à l'heure arrêter là parce que", 0.91827959, 0.5]

"""
#~ recognizeFromFile( strSoundFilename, strAnsiLang )
strPath = "D:/cherie_sound_classified/bruit/"
strPath = "D:/cherie_sound_classified/voix/"
recognizeFromFolder(strPath)
#~ sendInOneBigWav(strPath)
