"""
linux:
sudo apt install libportaudio2
pip install sounddevice

windows:
pip install sounddevice
(Normalement PortAudio est fourni avec le package Windows.)

"""
import sounddevice as sd

from audio_analyser import AudioAnalyser

import base64
import json
import os
import time


SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

def play_sound( soundfilename, bWaitEnd = True ):
    import winsound
    flag = winsound.SND_FILENAME
    if not bWaitEnd:
        flag |= winsound.SND_ASYNC
        
    winsound.PlaySound(soundfilename,  flag )

    

def send_audio(filename, user_id="tester_audio"):
    import http.client
    
    time_begin = time.time()

    with open( filename, "rb" ) as f:
        audio_data = f.read()

    conn = http.client.HTTPSConnection( "engrenage.studio", 45001 )

    conn.request(
        "POST",
        "/voice",
        body = audio_data,
        headers = {
            "Content-Type": "audio/wav",
            "X-User-Id": user_id
        }
    )

    response = conn.getresponse()

    data = response.read()

    content_type = response.getheader("Content-Type", "")
    
    print( "INF: duration before start of play: %.2fs" % (time.time() - time_begin) )

    if content_type.startswith("audio/wav"):
        # Reponse TTS
        print("INF: reponse audio, %.2f KB" % (len(data) / 1024))

        #~ texte = response.getheader("X-Text")
        text_b64 = response.getheader("X-Text-B64")
        texte = base64.b64decode(text_b64).decode("utf-8")
        print("Texte reponse:", texte)
        
        if os.name == "nt":
            import winsound
            winsound.PlaySound( data, winsound.SND_MEMORY )

        with open("/tmp/response_%d.wav" % int(time.time()), "wb") as f:
            f.write(data)

        # ici tu peux jouer response.wav
        # ou traiter directement data

    else:
        # Reponse JSON normale (juste du texte)
        data = json.loads(data.decode("utf-8"))

        print(data)
        print(data["ans"])




def main():
    print( "INF: Main: Starting acquiring..." )
    
    analyser = AudioAnalyser( sample_rate = SAMPLE_RATE, channels = CHANNELS, sample_width = 2 )

    def audio_callback( indata, frames, time_info, status ):

        if status:
            print( status )

        audio_data = indata.copy().tobytes()

        filename = analyser.receive_audio_buffer( audio_data )

        if filename:
            print( "Speech saved to:", filename )
            play_sound( "datas/singingbowl_84_short.wav", False )
            send_audio( filename )
            play_sound( "datas/bowl_start.wav" )

    print( "Main: Starting microphone..." )

    with sd.InputStream(
        samplerate = SAMPLE_RATE,
        channels = CHANNELS,
        dtype = "int16",
        blocksize = CHUNK_SIZE,
        callback = audio_callback
    ):
        print( "Listening..." )
        
        play_sound( "datas/bowl_start.wav" )

        while True:
            sd.sleep( 1000 )


if __name__ == "__main__":
    main()
