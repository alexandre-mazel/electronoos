# -*- coding: cp1252 -*-
import io
import os
import pocketsphinx
import speech_recognition
import time

import misctools

recognizer = speech_recognition.Recognizer()

#~ self.strDstPath = "/tmp/";
if os.name == "nt":
    strVerbatimPath = "c:/save/"
else:
    strVerbatimPath = os.path.expanduser("~/save/")
    
try:
    os.makedirs( strVerbatimPath )
except: pass
strVerbatimFilename = strVerbatimPath+"verbatim.txt"

def storeVerbatim(recognized):
    timestamp = misctools.getTimeStamp()
    f = io.open(strVerbatimFilename,"a",encoding="cp1252")
    f.write("%s: %s\n" % (timestamp,str(recognized)) )
    f.close()

def recognizeFromFile( filename, language = "en-US", bUseSphinx = 1):
    """
    return recognised_sentence,score,proba
    """
    bVerbose = 1
    bVerbose = 0
    retVal = None

    with speech_recognition.WavFile(filename) as source:
        audio = recognizer.record(source) # read the entire WAV file
    # recognize speech using  Speech Recognition
    
    try:
        timeBegin = time.time()
        bShowAll = 0
        bShowAll = 1
        
        if not bUseSphinx:
            #~ import sound_processing
            #~ retFromReco = sound_processing.getSpeechInWav(filename)
            retFromReco = recognizer.recognize_google(audio, language = language, show_all = bShowAll)
            
            if bVerbose: print( "retFromReco: %s" % str(retFromReco) )

        else:
            keyword_entries = None
            retFromReco = recognizer.recognize_sphinx(audio, language = language, keyword_entries=keyword_entries, show_all = bShowAll )
            if bVerbose: print("Duration: %.3fs" % (time.time()-timeBegin))
            if bVerbose: print( "retFromReco: %s" % str(retFromReco) )
            
            if bShowAll:
                #~ if bVerbose: print( "retFromReco: dir %s" % str(dir(retFromReco.hyp()) ))
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
    if retVal != None: 
        # store a verbatim of the conversation
        storeVerbatim(retVal)

    return retVal
    
# recognizeFromFile - end
