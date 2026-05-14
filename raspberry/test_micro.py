import microphone
import numpy as np
import types

config = types.SimpleNamespace()
config.MIC_RATE = 48000
config.FPS = 30
config.min_treshold = 1e-7
config.N_ROLLING_HISTORY = 2

def microphone_update( audio_samples ):
    global y_roll, prev_rms, prev_exp, prev_fps_update
    # Normalize samples between 0 and 1
    y = audio_samples / 2.0**15
    # Construct a rolling window of audio samples
    #~ y_roll[:-1] = y_roll[1:]
    #~ y_roll[-1, :] = np.copy(y)
    #~ y_data = np.concatenate(y_roll, axis=0).astype(np.float32)
    
    vol = np.max(np.abs(y))
    avg = np.mean(np.abs(y))
    print("DBG: microphone_update: max: %5.3f, avg: %5.3f" % (vol,avg) )
    return
    if vol < config.min_treshold:
        print('No audio input. Volume below threshold. Volume:', vol)
        #~ led.pixels = np.tile(0, (3, config.N_PIXELS))
        #~ led.update()
    else:
        # Transform audio input into the frequency domain
        N = len(y_data)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N
        # Pad with zeros until the next power of two
        y_data *= fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * dsp.mel_y.T
        # Scale data to values more suitable for visualization
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= mel_gain.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip
        #~ output = visualization_effect(mel)
        #~ led.pixels = output
        #~ led.update()
        if 0: # config.USE_GUI:
            # Plot filterbank output
            x = np.linspace(config.MIN_FREQUENCY, config.MAX_FREQUENCY, len(mel))
            mel_curve.setData(x=x, y=fft_plot_filter.update(mel))
            # Plot the color channels
            r_curve.setData(y=led.pixels[0])
            g_curve.setData(y=led.pixels[1])
            b_curve.setData(y=led.pixels[2])
            
    return
    if config.USE_GUI:
        app.processEvents()
    
    if config.DISPLAY_FPS:
        fps = frames_per_second()
        if time.time() - 0.5 > prev_fps_update:
            prev_fps_update = time.time()
            print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))
            
            
def sounds_update( audio_samples_multi ):
    """
    receive a list of channel, for each channel a list audio_samples
    """
    vols = []
    avgs = []
    for i, audio_samples in enumerate(audio_samples_multi):
        y = audio_samples / 2.0**15
        vol = np.max(np.abs(y))
        avg = np.mean(np.abs(y))
        vols.append(vol)
        avgs.append(avg)
    
    print("DBG: sounds_update: ", end = "")      
    for i,vol in enumerate(vols):
        print("max: %5.3f, avg: %5.3f" % (vol,avgs[i]), end="" )
    print("")
        
# sounds_update - end


# Number of audio samples to read every time frame
samples_per_frame = int(config.MIC_RATE / config.FPS)


# Array containing the rolling audio sample window
y_roll = np.random.rand(config.N_ROLLING_HISTORY, samples_per_frame) / 1e16

# Start listening to live audio stream (1)
#~ microphone.start_stream(microphone_update,config.MIC_RATE, config.FPS )

microphone.start_stream_multi(sounds_update,config.MIC_RATE, config.FPS )

