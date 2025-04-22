# -*- coding: utf-8 -*-
import sys
sys.path.append("../alex_pytools/")
import wav

from matplotlib import pyplot as plt

from scipy.fftpack import fft
#from scipy.io import wavfile # todo: look at it one time
import numpy as np
import librosa

def compute_fft( wavdata, nNbrBitsPerSample = 16 ):
    """
    Analyse the sound between timeStartSec and timeStopSec
    """
    if nNbrBitsPerSample == 8:
        data = [(ele/2**8.)*2-1 for ele in wavdata] # this is 16-bit track, b is now normalized on [-1,1)
    elif nNbrBitsPerSample == 16:
        data = [(ele/2**16.)*2-1 for ele in wavdata] # this is 16-bit track, b is now normalized on [-1,1)
    window_size = 1024*4
    start = 0
    f_avg = fft(data[start:start+window_size]) # calculate fourier transform (complex numbers list)
    start += window_size
    cpt = 1
    while start + window_size <= len(data):
        f = fft(data[start:start+window_size])
        f_avg += f
        #~ print("len f_avg:", len(f_avg) )
        start += window_size
        cpt += 1
    f_avg /= cpt
    
    maxi = np.argmax(f_avg)
    print("maxi: %s" % maxi )
        
    return f_avg[len(f_avg)//2:] # keep only first part of the simmetry
    
def compute_mfcc( wavdata, samplerate = 44100 ):
    data = [(ele/2**16.)*2-1 for ele in wavdata] # this is 16-bit track, b is now normalized on [-1,1]
    data = np.array(data)
    
    window_size = 4096*2
    block_of_interest = 0
    
    start = 0
    f_avg = librosa.feature.melspectrogram( data[start:start+window_size], sr=samplerate,n_fft=2048,hop_length=2048,center=False)
    f_avg = f_avg[block_of_interest]
    
    start += window_size
    cpt = 1
    while start + window_size <= len(data):
        f = librosa.feature.melspectrogram( data[start:start+window_size], sr=samplerate,n_fft=2048,hop_length=2048,center=False)
        f = f[block_of_interest]
        f_avg += f
        #~ print("len f_avg:", len(f_avg) )
        start += window_size
        cpt += 1
    f_avg /= cpt
    
    return f_avg

def analyse_portion( wav_object, timeStartSec = 0., timeStopSec = 1. ):
    """
    Analyse the sound between timeStartSec and timeStopSec
    """
    print( "DBG: analyse_portion between %.2fs and %.2fs" % (timeStartSec,timeStopSec) )
    sample_per_sec = wav_object.nAvgBytesPerSec//(wav_object.nNbrBitsPerSample//8)
    print( "DBG: analyse_portion: sample_per_sec: %s" % (sample_per_sec) )
    start_portion = int(timeStartSec*sample_per_sec)
    stop_portion = int(timeStopSec*sample_per_sec)
    extract = wav_object.data[start_portion:stop_portion]
    print( "DBG: analyse_portion from data at %d and %d" % (start_portion,stop_portion) )
    # mono-ify
    if wav_object.nNbrChannel == 2:
        extract = extract[::2]
    print( "DBG: analyse_portion: extract has len of %d" % len(extract))
    
    if 0:
        f = open("/tmp/t%03d.raw" % int(timeStartSec),"wb")
        extract.tofile(f)
        f.close()
        #~ exit(1)
    
    out = compute_fft(extract)
    #~ out = compute_mfcc(extract)
    
    out = out[100:300] # seul les premieres frequences pourraient etre interessantes
    
    
    if 0:
        plt.subplot(311)
        p1 = plt.plot(range(len(out)), out, "g") # plotting the signal
        plt.show()
    
    #print(out[:20])

    return out
    
def compute_dist( a1 ,a2 ):
    """
    compute dist between two array of same size
    """
    d = 0
    #~ print( "DBG: compute_dist: len 1: %d, len 2: %d" % (len(a1),len(a2)) )
    for i in range(len(a1)):
        #d += abs(a2[i]-a1[i])
        d += (a2[i]-a1[i])*(a2[i]-a1[i])
        #~ if i > 50:
            #~ break
    return d
    
def diarize_auto( asr_filename, wav_filename, dst_filename ):
    """
    receive a filename generated automatically by an asr and a wav, and will replace all ?:
    - filename with asr contents:
[11.860 --> 18.260]:  vous animiez un atelier sur la sécurité la sécurisation dans Capital je me souviens à peu près
  temper: 0.00, avg_logprob: -0.22, expprob: 0.81,  compression_ratio: 1.51, no_speech_prob: 0.16

[18.260 --> 19.640]:  ah oui d'accord

    - will output:
A: Vous animiez un atelier sur la sécurité la sécurisation dans Capital je me souviens à peu près
P: Ah oui d'accord

    """
    print("INF: diarize_auto: Loading sound...")
    w = wav.Wav(wav_filename)
    print("INF: diarize_auto: loaded sound of %.2fs (%.2fmin)" % (w.getDuration(), w.getDuration()/60 ) )
    print(w)
    ref1 = analyse_portion(w,69,73)
    ref2 = analyse_portion(w,184,186)
    d_ref = compute_dist(ref1,ref2)
    print("d_ref1 and 2: %.3f" % d_ref )
    
    ref1b = analyse_portion(w,70,72)
    ref2b = analyse_portion(w,185,185.5)
    print("dist_ref1 and ref1b: %.3f" % compute_dist(ref1,ref1b) )
    print("dist_ref2 and ref2b: %.3f" % compute_dist(ref2,ref2b) )
    print("dist_ref1b and ref2b: %.3f" % compute_dist(ref1b,ref2b) )
    
    if 0:
        for i in range(30):
            freqs = analyse_portion(w,i,i+1)
            print(freqs)
            d_ref1 = compute_dist(ref1,freqs)
            print("d_ref1: %.3f" % d_ref1 )
            d_ref2 = compute_dist(ref2,freqs)
            print("d_ref2: %.3f" % d_ref2 )
    listrange = [
            [0,0.000,5.700],
            [0,5.700, 6.88],
            [0,111.920,113.080],
            [1,7.98, 8.7],
            [1,16.400, 17.540],
            [1,130.880,134.660],
    ]
    print("\nstart verite terrain")
    for id,start,stop in listrange:
        freqs = analyse_portion(w,start,stop)
        d_ref1 = compute_dist(ref1,freqs)
        print("d_ref1: %.3f" % d_ref1 )
        d_ref2 = compute_dist(ref2,freqs)
        print("d_ref2: %.3f" % d_ref2 )
        id_computed = -1
        ratio = d_ref1/d_ref2
        print("ratio: %.2f" % ratio )
        if ratio < 0.8:
            id_computed = 0
        elif ratio > 1.2:
            id_computed = 1
        print("id reel: %d, computed: %d" % (id,id_computed) )
        
    
# diarize_auto - end

path = "/Users/alexa/perso/docs_nextcloud_edu/2024_09_DU_inspe/memoire_docs/record/"
asrf = path + "capyt.out"
wavf = path + "capyt.wav"
outf  = path + "capyt_diar.txt"
diarize_auto( asrf,wavf,outf)