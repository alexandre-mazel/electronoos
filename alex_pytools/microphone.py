"""
PyAudio Example: Make a wire between input and output (i.e., record a
few samples and play them back immediately).
"""
import numpy as np
import pyaudio # python -m pip install pyaudio
import time

import sound_processing

global_bMustStop = False

def stop_loop():
    global global_bMustStop
    global_bMustStop = True

def loop_getsound(callback=None):
    """
    start a loop, calling callback
    - callback: a function receiving buffer, rate, bytes, channel
    """

    CHUNK = 1024
    WIDTH = 2
    CHANNELS = 2
    RATE = 44100
    
    p = pyaudio.PyAudio()
    
    global global_bMustStop
    global_bMustStop = False
    
    bTestInOut = True # test monitor
    bTestInOut = False
    
    if bTestInOut:

        stream = p.open(format=p.get_format_from_width(WIDTH),
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=bTestInOut,
                        frames_per_buffer=CHUNK)

        print("DBG: monitoring in=>out")
        
        # 10 second of read and write to create reverb/larsen
        for i in range(0, int(RATE / CHUNK * 7)):
            data = stream.read(CHUNK)  #read audio stream
            stream.write(data, CHUNK)  #play back audio stream
        return

    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=bTestInOut,
                    frames_per_buffer=CHUNK)
    print("INF: loop_getsound: starting")


    cpt = 0
    while 1:
        data = stream.read(CHUNK)  # read audio stream (chunk = nbr sample)
        if global_bMustStop:
            break
        if callback != None: callback(data,RATE,WIDTH,CHANNELS,time.time())
        cpt += 1
        if (cpt%(5*RATE//CHUNK))==0:
            print("%.2f: received buffers: %d" % (time.time(),cpt))

    print("INF: loop_getsound: stopping")

    stream.stop_stream()
    stream.close()

    p.terminate()
# loop_getsound - end

def analyse_sound_just_peek(buffer,rate,width,channels,timestamp):
    # monotise le son
    #~ print("DBG: analyse_sound: rate: %s, width: %s, channels: %s, buffer len: %s" % (rate,width,channels,len(buffer)))
    aSoundData = np.fromstring( buffer, dtype = np.int16 )
    if channels>1 and 0:
        # keep only first one:
        aSoundData = aSoundData[::2] # ne semble pas reduire le buffer, bizarre!
        #~ print("DBG: analyse_sound: buffer len: %s" % len(buffer))
    
    nEnergy = sound_processing.computeEnergyBestNumpy(aSoundData);
    if nEnergy > 1:
        # 4-6: jardinier dans le jardin arriere:
        # 3-4: ventilo
        print( "nEnergy: %s" % nEnergy )
# analyse_sound - end

def analyse_sound_total(buffer,rate,width,channels,timestamp):
    import sound_analysis
    sound_analysis.soundAnalyser.processBuffer(buffer,rate,width,channels,timestamp)
    
def loopProcess(wordsCallback):
    import sound_analysis
    sound_analysis.soundAnalyser.setWordsHeardCallback(wordsCallback)
    loop_getsound(analyse_sound_total)
    
if __name__ == "__main__":
    loop_getsound(analyse_sound_just_peek)
    #~ loop_getsound(analyse_sound_total)