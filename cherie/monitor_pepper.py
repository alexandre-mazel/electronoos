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

while 1:
    speech_detected = mem.getData("Audio/SpeechDetected")
    if speech_detected != prev_speech_detected:
        print("%s: speech_detected: %s" % (misctools.getTimeStamp(),speech_detected) )
        prev_speech_detected = speech_detected
        
    sound_receiver_pause = mem.getData("sound_receiver_pause")
    if sound_receiver_pause != prev_sound_receiver_pause:
        print("%s: sound_receiver_pause: %s" % (misctools.getTimeStamp(),sound_receiver_pause) )
        prev_sound_receiver_pause = sound_receiver_pause
        
    rTempKneePitch = mem.getData("Device/SubDeviceList/KneePitch/Temperature/Sensor/Value")
    if rTempKneePitch != rPrevTempKneePitch:
        print("%s: \t\trTempKneePitch: %s" % (misctools.getTimeStamp(),rTempKneePitch) )
        rPrevTempKneePitch = rTempKneePitch
        
    rTempHipPitch = mem.getData("Device/SubDeviceList/HipPitch/Temperature/Sensor/Value")
    if rTempHipPitch != rPrevTempHipPitch:
        print("%s: rTempHipPitch: %s" % (misctools.getTimeStamp(),rTempHipPitch) )
        rPrevTempHipPitch = rTempHipPitch
        
        
    
    time.sleep(0.05)
    