import sys

from queue import Queue

from sounddevice import InputStream
from soundfile import SoundFile

fs = 44100
channels = 2
device1 = 1
device2 = 2


def create_callback(q):

    def callback(data, frames, time, status):
        if status:
            print(status)
        q.put(data.copy())

    return callback


q1 = Queue()
q2 = Queue()

stream1 = InputStream(
    device=device1,
    samplerate=fs,
    channels=channels,
    callback=create_callback(q1),
)
stream2 = InputStream(
    device=device2,
    samplerate=fs,
    channels=channels,
    callback=create_callback(q2),
)

sf1 = SoundFile(
    file=f"rec_device_{device1}.wav",
    mode="w",
    samplerate=int(stream1.samplerate),
    channels=stream1.channels,
)
sf2 = SoundFile(
    file=f"rec_device_{device2}.wav",
    mode="w",
    samplerate=int(stream2.samplerate),
    channels=stream2.channels,
)

with sf1, sf2:
    with stream1, stream2:
        print("press Ctrl+C to stop the recording")
        interrupted = False
        try:
            while not interrupted:
                sf1.write(q1.get())
                sf2.write(q2.get())
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            interrupted = True
            q1.task_done()
            q2.task_done()
            #~ exit(1)
            sys.exit() # argh rien ne nous kill