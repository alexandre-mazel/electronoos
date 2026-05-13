import pyaudio
import math
import numpy as np
import time

import dmxal

def get_device_by_name( name, verbose = 1 ):
    """
    return device index,name or -1,"" if not found
    """
    audio = pyaudio.PyAudio()

    if verbose: print("----------------------record device list---------------------")
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                dev_name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
                if verbose: print("Input Device id ", i, " - ", dev_name )
                if name in dev_name:
                    if verbose: print("FOUND")
                    return i,dev_name
    return -1,""


def analyse_microphone_input():

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    RECORD_SECONDS = 5
    device_index = 2
    audio = pyaudio.PyAudio()
    
    index,device_name = get_device_by_name( "microphone")
    
    nNbrChannel = 4;
    dmx = dmxal.DMX( num_of_channels = nNbrChannel )
    dmx_id = 1
    for i in range(4):
        dmx.set_data( dmx_id+i, 255 )

    #~ index = int(input())
    
    print("INF: analyse_microphone_input: recording using device: %d:\n%s" % (index,device_name) )

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,input_device_index = index,
                    frames_per_buffer=CHUNK)
    print ("recording started")
    Recordframes = []
    
    rmoyavg = 0
     
    while 1:
        data = stream.read(CHUNK)
        #~ print("DBG: analyse_microphone_input: data len: %s, type: %s" % (len(data),type(data) ) ) # 1024 bytes (2*512 int16)
        d = np.fromstring(data, dtype=np.int16)
        #~ print("DBG: analyse_microphone_input: d len: %s, type: %s" % (len(d),type(d) ) ) # 512, type: <class 'numpy.ndarray'>
        d = np.abs(d)
        maxi = d.max()
        rmaxi = maxi/2**15
        moy = d.mean()
        rmoy = moy/2**15
        rmoy *= 10
        if rmoy > 1:
            rmoy = 1
        #~ print("DBG: analyse_microphone_input: maxi: %d, %.2f" % (maxi,rmaxi) )
        print("DBG: analyse_microphone_input: maxi: %.2f, moy: %.2f, moyavg: %.2f" % (rmaxi,rmoy,rmoyavg) )
        
        # rmoyavg: une energie qui redescend petit a petit
        
        if rmoyavg < rmoy:
            rmoyavg = rmoy
        else:
            rmoyavg *= 0.99

        dmx.set_data( dmx_id+0, int(rmaxi*255), auto_send=False )
        dmx.set_data( dmx_id+1, int(rmoyavg*255), auto_send=False )
        dmx.set_data( dmx_id+2, int(time.time()*10)%255, auto_send=False ) # chaque 25s ca redevient rouge d'un coup et puis ca blanchit
        dmx.set_data( dmx_id+3, int(time.time()*10)%255 )
        
    print ("recording stopped")
     
    stream.stop_stream()
    stream.close()
    audio.terminate()

    
analyse_microphone_input()