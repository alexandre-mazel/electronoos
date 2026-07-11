import datetime
import sys
from os.path import join
from queue import Queue
from threading import Thread
# essai avec multiprocessing:
#~ from multiprocessing import Process
#~ Thread = Process

from sounddevice import InputStream
from soundfile import SoundFile

import numpy
import numpy as np


import rpi_leds

def getTimeStamp():
    """
    
    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def log( msg ):
    fn = "/home/na/log/fossi.log"
    fn = open(fn,"at")
    fn.write( getTimeStamp() + ": " + msg + "\n" )
    fn.close()
    


def file_writing_thread(*, q, **soundfile_args):
    """Write data from queue to file until *None* is received."""
    # NB: If you want fine-grained control about the buffering of the file, you
    #     can use Python's open() function (with the "buffering" argument) and
    #     pass the resulting file object to sf.SoundFile().
    with SoundFile(**soundfile_args) as f:
        while True:
            data = q.get()
            if data is None:
                break
            f.write(data)
            
def arr_to_str(a,limit_nbr=99999):
    s = ""
    for num, e in enumerate(a):
        s += "%.2f," % e
        if num >= limit_nbr-1:
            break
    return s


buf = np.ndarray( shape=(1,4), dtype=np.float32 ) # with 4 random value at start

avg = [0,0,0,0]
nbr_callback = 0
strip = None

def record_device(device_id):
    
    def audio_callback(data, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        global buf, avg, nbr_callback, strip
        #~ if status:
            #~ print(status, file=sys.stderr)
        #~ audio_q.put(data.copy())
        #~ print("%s:%s" % (len(data[0]), frames) )
        #~ print(device_id,end="",flush=True)
        #~ print("type:", type(data)) # numpy.ndarray
        #~ print("type:", type(data[0]), flush=True) # numpy.ndarray
        #~ print("type:", type(data[0][0])) # float32
        # data is a list of sample, for each sample 2 or 4 value (one per channel)
        
        nbr_callback += 1
        
        if nbr_callback < 1000:
            return # skip first buffers with cheat(s)
            
        if nbr_callback & 0x1 != 0:
            return # keep only one on a lot of them
            
        if 0:
            # analyse on the fly, but buffer doesn't have all same length (from 23 to 384)
            moy = np.abs(data).mean(axis=0) # axis=0 => mean for each channel
            maxi = data.max(axis=0)
            print( "moy: %s, maxi: %s" % (arr_to_str(moy),arr_to_str(maxi)) )
        else:
            # buffer them and analyse from time to time
            buf = np.concatenate((buf,data))
            size_analyse = 1024
            if len(buf) > size_analyse:
                bufana = buf[:size_analyse]
                buf = buf[size_analyse:]
                moy = np.abs(bufana).mean(axis=0) # axis=0 => mean for each channel
                maxi = abs(bufana.max(axis=0))

                for i in range(4):
                    coef = 0.99 # resilience coef
                    coef = 0.9
                    avg[i] = avg[i] * coef + maxi[i] * (1-coef)
                    
                lim_print = 4
                out = "moy:%s max:%s avg:%s" % ( arr_to_str(moy,lim_print), arr_to_str(maxi,lim_print), arr_to_str(avg,lim_print) )
                print(  out )
                
                leds = [0,0,0,0]
                for i in range(4):
                    val = min(255,int(avg[i]*200))
                    val = min(val,255)
                    #~ val = 12
                    leds[i] = val
                    
                if 0:
                    # indic la valeur
                    print( "leds: %s" % leds )
                    for i in range(255):
                        #~ strip.setPixelColor(i, val<<24)
                        strip.setPixelColor( i, 0xFFFFFFFF if i in leds else 0 )
                else:
                    val = min(255,int(avg[3]*200*4))
                    print("val: %s" % val )
                    #~ log( out + "val: " + str(val) )
                    color = val<<24
                    for i in range(rpi_leds.nbr_leds):
                        #~ strip.setPixelColor(i, val<<24)
                        strip.setPixelColor( i, color )                    
                strip.show()
            
    file_name = join(rec_dir, f"rec_dev{device_id}_ch{channels}.wav")

    print("#" * 40)
    stream = InputStream(
        samplerate=fs, device=device_id, channels=channels, callback=audio_callback
    )
    stream.start()
    print(f"started stream {stream} ...")

    audio_q = Queue()
    print(f"generated queue {audio_q} ...")

    thread = Thread(
        target=file_writing_thread,
        kwargs=dict(
            file=file_name,
            mode="w",
            samplerate=int(stream.samplerate),
            channels=stream.channels,
            q=audio_q,
        ),
    )
    thread.start()
    print(f"started thread {thread} ...")
    print(f'recording file "{file_name}" ...')
    print("#" * 40)


if __name__ == "__main__":
    fs = 44100
    channels = 2
    channels = 4
    rec_dir = "./"
    
    log( "start" )
    
    strip = rpi_leds.init_strip(rpi_leds.nbr_leds)

    try:
        record_device(device_id=1) # record channel 1 et 2
        #~ record_device(device_id=2) # record channel 3 et 4 (but thread not updated!)

        print("press Ctrl+C to stop the recording")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        exit(0)
    except Exception as e:
        exit(type(e).__name__ + ": " + str(e))