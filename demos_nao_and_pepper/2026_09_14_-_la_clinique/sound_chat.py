# -*- coding: utf-8 -*-

from naoqi import ALModule, ALProxy, ALBroker
import qi
import sys


class AudioModule(ALModule):

    def __init__(self, name):
        print( "INF: AudioModule: initing..." )
        ALModule.__init__(self, name)

        self.audio = ALProxy("ALAudioDevice")

        # Configuration :
        # 16000 Hz
        # 4 microphones
        # 0 = pas de décalage temporel
        # 0 = pas de gain supplémentaire
        self.audio.setClientPreferences(
            self.getName(),
            16000,
            3,       # 3 = 4 microphones
            0
        )

        self.audio.subscribe(self.getName())

        print("Audio subscription started")

    def processRemote(self, nbOfChannels, nbrOfSamplesByChannel, timeStamp, buffer):

        print("Channels :", nbOfChannels)
        print("Samples/channel :", nbrOfSamplesByChannel)
        print("Timestamp :", timeStamp)

        # buffer contient les échantillons audio.
        #
        # Avec 4 microphones, les données sont entrelacées :
        #
        # mic0, mic1, mic2, mic3,
        # mic0, mic1, mic2, mic3, ...

        print("Buffer length :", len(buffer))

        # Exemple : afficher les premiers échantillons
        print("First samples:", buffer[:20])
        
    def stop(self):
        self.audio.unsubscribe(self.getName())


if __name__ == "__main__":

    IP = "localhost"
    PORT = 9559

    # Connexion au broker NAOqi
    myBroker = ALBroker(
        "myBroker",
        "0.0.0.0",
        0,
        IP,
        PORT
    )

    module = AudioModule("AudioModule")

    try:
        raw_input("Press ENTER to stop...\n")
    except KeyboardInterrupt:
        pass

    module.audio.unsubscribe(module.getName())
    myBroker.shutdown()
