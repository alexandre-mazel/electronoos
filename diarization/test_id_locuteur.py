import sys
sys.path.append("../alex_pytools/")
import wav
import librosa

def extract_features_sound( filename ):
    
    w = wav.Wav()
    w.load( filename )
    
    pos = 0
    windowsize = 2048*2
    while pos < w.nNbrSample:
        print("pos: %s" % pos )
        n = int(pos * w.nSamplingRate)#+windowsize//2 # heard sound is centered to window
        
        try:
            m_block = librosa.feature.melspectrogram(w.data[n:n+windowsize], sr=w.nSamplingRate,n_fft=windowsize,hop_length=windowsize,center=False)
        except librosa.util.exceptions.ParameterError as err:
            print("WRN: extract_features_sound: err: %s" % str(err))
            return
        
        print(m_block)
        S_dB = librosa.power_to_db(m_block, ref=np.max)
        print(S_dB)
        
extract_features_sound("user_alex_1.wav")
        