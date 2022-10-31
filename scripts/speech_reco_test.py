import speech_recognition
import pocketsphinx

# install fr
"""
you have to rename and restructure the files in the language zip folder:

etc/voxforge_it_sphinx.lm > speech_recognition/pocketsphinx-data/fr-FR/language-model.lm.bin
etc/voxforge_it_sphinx.dic > speech_recognition/pocketsphinx-data/fr-FR/pronounciation-dictionary.dict
model_parameters/voxforge_it_sphinx.cd_cont_2000/ > speech_recognition/pocketsphinx-data/fr-FR/acoustic-model/
"""


strSoundFilename = "C:/tmp/sieste.wav"
strSoundFilename = "C:/Users/alexa/dev/git/electronoos/alex_pytools/autotest_data/la_sieste2.wav" # fr
strAnsiLang = "fr-FR"

if 1:
    # en
    strSoundFilename = "C:/Users/alexa/dev/git/electronoos/cherie/test_brice.wav"
    strAnsiLang = "en-US"
    
    

if 1:
    from pocketsphinx import LiveSpeech
    for phrase in LiveSpeech(language = strAnsiLang):
        print(phrase)
    
if 0:
    # play it:
    import sys
    sys.path.append("../alex_pytools/")
    import sound_player
    sound_player.soundPlayer.playFile(strSoundFilename,bWaitEnd=1)

r = speech_recognition.Recognizer()
print(dir(r))

retVal = None

with speech_recognition.WavFile(strSoundFilename) as source:
    audio = r.record(source) # read the entire WAV file
# recognize speech using  Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    retFromReco =r.recognize_sphinx(audio, language = strAnsiLang, show_all = True )
    print( "retFromReco: %s" % print(dir(retFromReco)) )
    print( "retFromReco: %s" % str(dir(retFromReco.hyp()) ))
    print( "retFromReco3: prob: %s" % str(retFromReco.hyp().prob ) )
    print( "retFromReco3: score: %s" % str(retFromReco.hyp().score ) )
    print( "retFromReco3: best_score: %s" % str(retFromReco.hyp().best_score ) )
    print( "retFromReco3: hypstr: %s" % str(retFromReco.hyp().hypstr ) )
    if retFromReco != []:
        
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
    
if retVal == None: print("Speech Recognition could not understand audio\n")

print("DBG: retVal: %s" % str(retVal) )