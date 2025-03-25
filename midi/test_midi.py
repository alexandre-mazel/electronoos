import mido # pip install mido (eg 1.3.3)
import rtmidi # pip install python-rtmidi (required by mido)

 # cf https://mido.readthedocs.io/en/stable/

#~ print(dir(mido))

# print all informations from Nano Kontrol2 (works!)
with mido.open_input() as inport:
    for msg in inport:
        print(msg)
        

# Korg Nano Kontrol 2: work directly (PnP style)
# will issue value from control 0 to 71.
# 0..127 for potar and slider, 127 when button is down