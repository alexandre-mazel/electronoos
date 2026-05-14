import sys
from os.path import join
from queue import Queue
from threading import Thread
# essai avec multiprocessing:
#~ from multiprocessing import Process
#~ Thread = Process

from sounddevice import InputStream
from soundfile import SoundFile

import numpy  # Make sure NumPy is loaded before it is used in the callback

assert numpy  # avoid "imported but unused" message (W0611)


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


def record_device(device_id):
    def audio_callback(data, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        audio_q.put(data.copy())
        print(device_id,end="",flush=True)

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
    channels = 4 # j'ai tente avec 4 chan et un seul device, et ca fonctionne !!!
    rec_dir = "./"

    try:
        record_device(device_id=1) # record channel 1 et 2
        #~ record_device(device_id=2) # record channel 3 et 4 (but thread not updated!)

        print("press Ctrl+C to stop the recording")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        exit(0)
    except Exception as e:
        exit(type(e).__name__ + ": " + str(e))