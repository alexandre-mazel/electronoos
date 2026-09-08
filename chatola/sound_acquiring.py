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

import json


SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

def send_audio(filename, user_id="tester_audio"):
    import http.client

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

    if content_type.startswith("audio/wav"):
        # Réponse TTS
        print("INF: réponse audio, %.2f KB" % (len(data) / 1024))

        texte = response.getheader("X-Text")
        print("Texte reponse:", texte)

        with open("/tmp/response.wav", "wb") as f:
            f.write(data)

        # ici tu peux jouer response.wav
        # ou traiter directement data

    else:
        # Réponse JSON normale
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
            send_audio( filename )

    print( "Main: Starting microphone..." )

    with sd.InputStream(
        samplerate = SAMPLE_RATE,
        channels = CHANNELS,
        dtype = "int16",
        blocksize = CHUNK_SIZE,
        callback = audio_callback
    ):
        print( "Listening..." )

        while True:
            sd.sleep( 1000 )


if __name__ == "__main__":
    main()
