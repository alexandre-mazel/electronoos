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


SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

def send_audio(filename):
    import http.client

    with open( filename, "rb" ) as f:
        audio_data = f.read()

    conn = http.client.HTTPSConnection(
        "https://engrenage.studio",
        45001
    )

    conn.request(
        "POST",
        "/voice",
        body = audio_data,
        headers = {
            "Content-Type": "audio/wav"
        }
    )

    response = conn.getresponse()

print( response.read().decode( "utf-8" ) )


def main():
    analyser = AudioAnalyser(
        sample_rate = SAMPLE_RATE,
        channels = CHANNELS,
        sample_width = 2
    )

    def audio_callback( indata, frames, time_info, status ):
        if status:
            print( status )

        audio_data = indata.copy().tobytes()

        filename = analyser.receive_audio_buffer(
            audio_data
        )

        if filename:
            print( "Speech:", filename )

    print( "Starting microphone..." )

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
