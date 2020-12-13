"""
process big wav file, cut them...
"""
import wav
import pygame_tools

import os
import time

import speech_recognition #pip install speechrecognition

def cleanText(rawResume):
    """ encode with bs4 for handle special character """
    soup = BeautifulSoup(rawResume)

    for script in soup(["script", "style"]):                                                
        script.extract()                                                                    
    
    text = soup.get_text()                                           
    lines = (line.strip() for line in text.splitlines())                       
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) 
    text = '\n'.join(chunk for chunk in chunks if chunk)                  
    text = text.encode('utf-8', 'ignore')
    return text
    
def cleanText2( txt ):
    try:
        txt = str(txt)
    except BaseException as err:
        print("DBG: cleanText2: can't convert text to ascii?" )
        try:
            txt = cleanText(txt)
        except:
#                    logging.warning("freespeech : analyse : you need to install beautifulsoup4")
            #Methode with "ai"
            unicoded = unicode(txt).encode('utf8')
            print("DBG: cleanText2: unicoded: %s" % unicoded )
            utxt = str(unicoded)
            print("DBG: cleanText2: txt: %s" % utxt )
            txt = ""
            for c in utxt:
                if ord(c) < 128:
                    txt += c
                else:
                    print("DBG: cleanText2: bad char: %s %d" % (c, ord(c) ) )
                    ordc = ord(c)
                    if( ordc in [168, 169, 170, 171] ):
                        txt += "ai"
                    if( ordc in [160] ):
                        txt += "a"
                    
        print("DBG: cleanText2: txt2: %s" % txt )
    return txt
        

def getSpeechInWav( strSoundFilename ):
    strAnsiLang = 'en-UK'
    strAnsiLang = 'fr-FR'
    retVal = None
    
    timeBegin = time.time()
    
    r = speech_recognition.Recognizer()
    
    with speech_recognition.WavFile(strSoundFilename) as source:
        audio = r.record(source) # read the entire WAV file
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        retFromReco =r.recognize_google(audio, language = strAnsiLang, show_all = True )
        print( "DBG: getSpeechInWav: retFromReco: %s" % retFromReco )
        if retFromReco != []:
            
            alt = retFromReco['alternative']
            strTxt = alt[0]['transcript']

            # when reco does not return a confidence, use -1 as an error code
            if 'confidence' in alt[0]:
                rConf = alt[0]['confidence']
            else:
                print( "DBG: getSpeechInWav: no confidence returned")
                rConf = -1.0
        
            strTxt = cleanText2( strTxt )
            print( "INF: getSpeechInWav: Google Speech Recognition thinks you said: '%s' (conf:%5.2f)\n" % (strTxt, rConf) )
            retVal = [ [strTxt,rConf] ]

    except speech_recognition.UnknownValueError:
        pass
        
    except speech_recognition.RequestError as e:
        print( "ERR: getSpeechInWav: Could not request results from Google Speech Recognition service; {0}".format(e))

    rProcessDuration = time.time() - timeBegin
    rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero

    if retVal == None: 
        print( "INF: getSpeechInWav: Google Speech Recognition could not understand audio\n")
        return ""
    
    return retVal[0][0]

def autocut(wavfile, rSilenceMinDuration = 0.3 ):
    w = wav.Wav(wavfile,bQuiet=False)
    print(w)
    #~ w.write("/tmp/t.wav")
    seq = w.split(rSilenceTresholdPercent=0.6,rSilenceMinDuration=rSilenceMinDuration)
    for i,s in enumerate(seq):
        s.normalise()
        name = "/tmp/s%03d.wav" % i 
        s.write(name)
        if 0:
            print("playing: %s" % name )
            pygame_tools.soundPlayer.playFile(name)
            time.sleep(0.5)
            
        if 1:
            txt = getSpeechInWav(name)
            newname = name.replace(".wav", "__" + txt[:100]+".wav")
            os.rename(name, newname)
            
    
    
    
if __name__ == "__main__":
    if 1:
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec2.wav")
        autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec1_fx.wav")
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec2_fx.wav",rSilenceMinDuration=0.5)
    if 0:
        strFile = "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec2/s032.wav"
        strFile = "/tmp/s032.wav"
        print(getSpeechInWav(strFile))
        pygame_tools.soundPlayer.playFile(strFile)
    
    
