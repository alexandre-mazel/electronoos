import os
import time
import wave
import audioop

import test_whisper


class AudioAnalyser:
    def __init__(
        self,
        sample_rate = 16000,
        channels = 1,
        sample_width = 2,
        vad_threshold = 700,
        silence_duration = 0.8,
        min_speech_duration = 0.3
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width

        self.vad_threshold = vad_threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration

        self.speech_buffer = bytearray()

        self.speech_active = False
        self.silence_time = 0.0
        self.speech_time = 0.0

        self.recordings_path = os.path.expanduser(
            "~/recordings/voice"
        )

        os.makedirs( self.recordings_path, exist_ok = True )

    def receive_audio_buffer( self, audio_data ):
        chunk_duration = len( audio_data ) / (
            self.sample_rate *
            self.channels *
            self.sample_width
        )

        level = audioop.rms(
            audio_data,
            self.sample_width
        )

        if level >= self.vad_threshold:
            if not self.speech_active:
                self.speech_active = True
                self.speech_time = 0.0
                self.silence_time = 0.0
                self.speech_buffer = bytearray()

            self.speech_buffer.extend( audio_data )

            self.speech_time += chunk_duration
            self.silence_time = 0.0

            return None

        if not self.speech_active:
            return None

        self.speech_buffer.extend( audio_data )
        self.silence_time += chunk_duration

        if self.silence_time < self.silence_duration:
            return None

        if self.speech_time < self.min_speech_duration:
            self.reset()
            return None

        filename = self.save_recording()

        self.reset()

        return filename

    def save_recording( self ):
        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        timestamp += "_%03d" % (
            int( ( time.time() % 1 ) * 1000 )
        )

        filename = os.path.join(
            self.recordings_path,
            "voice_%s.wav" % timestamp
        )

        with wave.open( filename, "wb" ) as wav:
            wav.setnchannels( self.channels )
            wav.setsampwidth( self.sample_width )
            wav.setframerate( self.sample_rate )
            wav.writeframes( bytes( self.speech_buffer ) )

        print( "saved:", filename )

        return filename

    def reset( self ):
        self.speech_buffer = bytearray()
        self.speech_active = False
        self.silence_time = 0.0
        self.speech_time = 0.0
        
# class AudioAnalyser - end

def loop_audio():
    audio_analyser = AudioAnalyser()
    whi = test_whisper.Whisper()

    while True:
        audio_chunk = microphone.read()

        filename = audio_analyser.receive_audio_buffer( audio_chunk )

        if filename:
            print( "speech detected:", filename )

            text = whi.analyse( filename )
            print( "TEXT:", text )
            
            
    
if __name__ == "__main__":  
    loop_audio()
