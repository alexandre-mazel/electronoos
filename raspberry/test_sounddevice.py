import sounddevice as sd  # sudo pip install sounddevice --break-system-packages
import soundfile as sf # sudo apt install python3-soundfile


print( sd.query_devices() )