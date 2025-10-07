import sounddevice as sd

# List available devices
print(sd.query_devices())
exit(0)

# Choose a specific input device by index or name
device_index = 2  # Example index (check your output from query_devices())

# Initialize the InputStream with that device
with sd.InputStream(device=device_index, channels=1, samplerate=44100) as stream:
    print("Recording from device:", device_index)
    data, overflowed = stream.read(1024)
    print("Received audio data:", data.shape)
    
    
"""
Avec la carte de Fossilation, On doit voir ca en user:

  0 bcm2835 Headphones: - (hw:2,0), ALSA (0 in, 8 out)
  1 UMC404HD 192k: USB Audio (hw:3,0), ALSA (4 in, 4 out)
  2 pulse, ALSA (32 in, 32 out)
* 3 default, ALSA (32 in, 32 out)

et ca en root:

< 0 bcm2835 Headphones: - (hw:2,0), ALSA (0 in, 8 out)
> 1 UMC404HD 192k: USB Audio (hw:3,0), ALSA (4 in, 4 out)


On va donc utiliser le 1!

"""

