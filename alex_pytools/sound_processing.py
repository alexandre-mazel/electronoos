"""
process big wav file, cut them...
"""
import wav
import misctools
try: import pygame_tools
except: pass


import os
import time

import speech_recognition #pip install speechrecognition

def cleanStringAnsi128( txt, bChangeSpaceAndQuote = True ):
    cleaned = ""
    for c in txt:
        newc=c
        if ord(c)>=128:
            oc = ord(c)
            if oc == 0xe0 or oc == 0xe2:
                newc = 'a'
            elif oc == 0xe7:
                newc = 'c'
            elif oc == 0xe8 or oc == 0xe9 or oc == 0xea:
                newc = 'e'
            elif oc == 0xee:
                newc = 'i'
            elif oc == 0xf4:
                newc = 'o'
            else:
                print("c: %s, 0x%x" % (c,ord(c)) )
                newc = "_"
        if bChangeSpaceAndQuote:
            if c in [ ' ',"'",'"', '-','?','/','\\']:
                newc = '_'
        cleaned += newc
    return cleaned

def cleanNameInFolder(strPath):
    """
    remove all not ascii 128 character in filename
    """
    listFile = sorted(  os.listdir(strPath) )
    for f in listFile:
        tf = strPath + f
        cleaned = cleanStringAnsi128(f)
        if cleaned != f:
            print("INF: %s => %s" % (f,cleaned) )
            os.rename(tf, strPath+cleaned)
            
            
def changeVolumeInFolder(strPath,rRatio=2):
    """
    remove all not ascii 128 character in filename
    """
    listFile = sorted(  os.listdir(strPath) )
    for f in listFile:
        tf = strPath + f
        print("INF: %s => %s * %5.1f" % ( f,f,rRatio ) )
        rNewDuration = wav.changeVolume( tf, rRatio )
            
            

def insertSilenceInFolder(strPath, rSilenceDuration):
    """
    add a silence to all wav in a folder
    """
    listFile = sorted(  os.listdir(strPath) )
    for f in listFile:
        tf = strPath + f
        rNewDuration = wav.insertSilenceAtBeginning(tf,rSilenceDuration)
        print("INF: %s: added %5.3fs resulting in a sound of %5.3fs" % (f,rSilenceDuration,rNewDuration) )
    

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
    
    if 1:
        # add silence before and after
        newname = misctools.getTempFilename() + ".wav"
        w = wav.Wav(strSoundFilename)
        w.ensureSilenceAtBegin(0.1)
        w.addSilence(0.1)
        w.write(newname)
        strSoundFilename = newname
    
    timeBegin = time.time()
    
    r = speech_recognition.Recognizer()
    
    with speech_recognition.WavFile(strSoundFilename) as source:
        audio = r.record(source) # read the entire WAV file
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        retFromReco =r.recognize_google(audio, language = strAnsiLang, show_all = True )
        #~ retFromReco =r.recognize_google_cloud(audio, language = strAnsiLang, show_all = True )
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
            
    except speech_recognition.UnknownValueError as e:
        print( "ERR: getSpeechInWav: Unknown Value Error; {0}".format(e))
    except speech_recognition.RequestError as e:
        print( "ERR: getSpeechInWav: Could not request results from Google Speech Recognition service; {0}".format(e))

    rProcessDuration = time.time() - timeBegin
    rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero

    if retVal == None: 
        print( "INF: getSpeechInWav: Google Speech Recognition could not understand audio\n")
        return ""
    
    return retVal[0][0]

def autocut(wavfile, rSilenceMinDuration = 0.3 ):
    bPlaySound = 0
    bAutoRename = 1
    bAlternativeManualInputted = 1
    bRemoveShortQuiet = 1
    bNormalise = 0
    strDstPath = "c:/generated/"
    
    print("INF: autocut, sound will be outputted to %s - no auto cleaning before!" % strDstPath )
    
    try: os.makedirs(strDstPath)
    except: pass
    
    nPeakRatioToKeep = 128 # 128 si respi a enlever, 16 sinon
    
    w = wav.Wav(wavfile,bQuiet=False)
    print(w)
    #~ w.write("/tmp/t.wav")
    seq = w.split(rSilenceTresholdPercent=0.6,rSilenceMinDuration=rSilenceMinDuration,nPeakRatioToKeep=nPeakRatioToKeep)
    print("INF: nbr part: %s" % len(seq) )
    for i,s in enumerate(seq):
        if bNormalise: s.normalise()
        
        name = "s_%04d.wav" % i 
        s.write(strDstPath+name)
        if bPlaySound:
            print("playing: %s" % name )
            pygame_tools.soundPlayer.playFile(strDstPath+name)
            time.sleep(0.1)
            
        if bAutoRename:
            txt = getSpeechInWav(strDstPath+name)
            if bAlternativeManualInputted:
                if txt == "":
                    # could be a short one
                    if bRemoveShortQuiet:
                        rDuration = s.getDuration()
                        rPeak = s.getPeakValue()
                        print("INF: Not recognized and peak: %4.2f duration is %5.2fs" % (rPeak,rDuration) )
                        if s.getDuration() < 2. and rPeak < 0.08:
                            os.unlink(strDstPath+name)
                            continue
                    if not bPlaySound:
                        print("playing: %s" % name )
                        pygame_tools.soundPlayer.playFile(strDstPath+name)
                        time.sleep(0.1)
                    txt = input("Type what you just heard:\n")
            if txt != "":
                newname = name.replace(".wav", "__" + txt[:100]+".wav")
                newname = cleanStringAnsi128(newname)
                print("INF: Renammed to '%s'\n" % newname )
                os.rename(strDstPath+name, strDstPath+newname)
            
# autocut - end
    
    
if __name__ == "__main__":
    strPathRavir = "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/"
    #~ strPathRavir = "d:/sounds/recordings/ravir"
    
    if 0:
        #~ changeVolumeInFolder(strPathRavir+"rec3/dial2/",2)
        changeVolumeInFolder(strPathRavir+"rec3/relance/",2)
    
    if 1:
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec2.wav")
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec1_fx.wav")
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/rec2_fx.wav",rSilenceMinDuration=0.5)
        #~ autocut("C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/robot3.wav")
        #~ autocut("D:/sounds/recordings/robot4.wav")
        #~ autocut("D:/sounds/recordings/respi1.wav") # should cut in 14 or 15 seq
        #~ autocut("D:/sounds/recordings/ravir3/r7.wav")
        autocut("D:/sounds/recordings/ravir3/r8_rel.wav")
        
    if 0:
        strFile = strPathRavir + "/rec2/s032.wav"
        strFile = "/tmp/s032.wav"
        strFile = "/generated/s0000__je.wav"
        #~ strFile = "/generated/s017__completement.wav"
        #~ strFile = "/generated/s0047__petit_pere.wav"
        print(getSpeechInWav(strFile))
        pygame_tools.soundPlayer.playFile(strFile)
        
    if 0:
        cleanNameInFolder(strPathRavir + "/rec1/")
        cleanNameInFolder(strPathRavir + "/rec2/")
        
    if 0:
        # add silence at beginning of each sound
        rTimeAdded = 0.1
        strPath = "/tmp2/brea/selected_intake/"
        strPath = "/home/nao/breath/selected_intake/"
        insertSilenceInFolder(strPath, rTimeAdded)
        insertSilenceInFolder("/home/nao/breath/selected_outtake/", rTimeAdded)
        
    
    
