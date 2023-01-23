import sys
import time

sys.path.append("../alex_pytools/")
import misctools

import naoqi
mem = naoqi.ALProxy("ALMemory", "localhost", 9559)
prev_speech_detected = -1
prev_sound_receiver_pause = -1
rPrevTempKneePitch = -1
rPrevTempHipPitch = -1
strPrevRecognizedWords = ""

timeLastErrorPrinted = time.time()-100

while 1:
    # todo: entrelarder d'un watch du log  /home/nao/agent_behavior_cherie.log
    speech_detected = mem.getData("Audio/SpeechDetected")
    if speech_detected != prev_speech_detected:
        print("%s: speech_detected: %s" % (misctools.getTimeStamp(),speech_detected) )
        prev_speech_detected = speech_detected
        
    sound_receiver_pause = mem.getData("sound_receiver_pause")
    if sound_receiver_pause != prev_sound_receiver_pause:
        print("%s: sound_receiver_pause: %s" % (misctools.getTimeStamp(),sound_receiver_pause) )
        prev_sound_receiver_pause = sound_receiver_pause
        
    try:
        strRecognizedWords = mem.getData("Audio/RecognizedWords")
        if strRecognizedWords != strPrevRecognizedWords:
            print("%s: strRecognizedWords: %s" % (misctools.getTimeStamp(),strRecognizedWords) )
            strPrevRecognizedWords = strRecognizedWords
    except RuntimeError:
        pass
            
    rTempKneePitch = mem.getData("Device/SubDeviceList/KneePitch/Temperature/Sensor/Value")
    if rTempKneePitch != rPrevTempKneePitch:
        print("%s: \t\trTempKneePitch: %s" % (misctools.getTimeStamp(),rTempKneePitch) )
        rPrevTempKneePitch = rTempKneePitch
        
    rTempHipPitch = mem.getData("Device/SubDeviceList/HipPitch/Temperature/Sensor/Value")
    if rTempHipPitch != rPrevTempHipPitch:
        print("%s: rTempHipPitch: %s" % (misctools.getTimeStamp(),rTempHipPitch) )
        rPrevTempHipPitch = rTempHipPitch
        
        
    time_send_lastUpdatingImage = mem.getData("updatingImage")
    #~ print(time_send_lastUpdatingImage)
    delay_updateImage = time.time()-time_send_lastUpdatingImage
    if delay_updateImage > 30:
        if time.time() - timeLastErrorPrinted > 5:
            timeLastErrorPrinted = time.time()
            print("WRN: delay_updateImage not updated since %.1fs" % delay_updateImage )
        
        
    
    time.sleep(0.05)
    