import time
import numpy as np
import pyaudio  # sudo apt install python3-pyaudio


def listAudioInDevices():
    """
    return a list of pair device_index, name
    """
    print("DBG: listAudioInDevices: starting...")
    
    # les lignes suivantes sortent pleins de garbages dans la sortie
    # avec pleins de probleme de Jack Server et de JackShm
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get( 'deviceCount' )
    
    listAll = []

    first = 0
    #~ first = 1
    for i in range(first, numdevices):
        print("INF: *** Testing device %s" % i )
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            listAll.append((i,p.get_device_info_by_host_api_device_index(0, i).get('name')))
            
    return listAll
    
def getDeviceByName(device_name):
    listDevices = listAudioInDevices()
    for idx,name in listDevices:
        if device_name in name:
            return idx
    print("WRN: getDeviceByName: device '%s' not found" % device_name )
    return -1
    


def start_stream(callback, mic_rate, fps):
    num_device = getDeviceByName("UMC404")
    
    p = pyaudio.PyAudio()
    frames_per_buffer = int(mic_rate / fps)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=mic_rate,
                    input=True,
                    frames_per_buffer=frames_per_buffer,
                    input_device_index= num_device )
    overflows = 0
    prev_ovf_time = time.time()
    while True:
        try:
            y = np.fromstring(stream.read(frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
            y = y.astype(np.float32)
            stream.read(stream.get_read_available(), exception_on_overflow=False)
            callback(y)
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    stream.stop_stream()
    stream.close()
    p.terminate()
