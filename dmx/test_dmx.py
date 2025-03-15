from dmxal import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
import dmxal
dmxal.set_verbose( True )

# Tested on Windows 10, amd64, Python 3.8
# Should also work on Linux, MacOS and on AARCH64 devices (ARM devices like Raspberry PI).
# Tested by Alexandre: 

# mon adaptateur:
#Veritable puce FTDI importee du Royaume-Uni. 
# Garantie de qualite 100 % garantie d'un an, entretien a vie
# Puce FT232RL + levier de vitesse RS485 avec la meilleure compatibilite et stabilite.
# Marque Czgor?
# 20euros ttc sur Amazon
# fonctionne pas
# detecte comme FTSER2K sur port Com20 (forcage sur port 2 (pourquoi mes ports 3-19 sont réservé?par qui?)
# dans FreeStyler X2: select DMXking USB DMX512-A?
# ou Eurolite USB-DMX512-interface/update-adapter

# Mes projos:
# 60 lumières Par LED DMX, lumière de scène RGB de 90W 
#angle de faisceau 25degrees
#7 canaux dmx: 
# mode de controle: auto/master/dmx512
# 31e amazon
# A001 Description:
# ch1: 0-255: Gradation totale
# ch2: 0: R fermé, 1-255: R ouvert
# ch3: 0: G fermé, 1-255: G ouvert
# ch4: 0: B fermé, 1-255: B ouvert
# ch5: 0-9: pas de strobo, 10-255: strobo lent a rapide
# ch6: 0-50: open dmx, 51-100: selection des couleurs du programme, 101-150: sauter pour
# ch7: vitesse
# 
#
#A DMX terminator helps to reduce ‘noise’ on the DMX chain, and makes the light respond to 
# control more accurately. It should be plugged in to the last fixture in any chain. For Terminator 
# connections please see below:
# cf le60_m.pdf
"""
An example from a Chinese LED PAR is the menu:
1. A001 DMX Channel Address (001-512) | 10CH mode
2. d001 DMX Channel Address (001-512) | 6CH mode 
"""
#
# avec logiciel: Freestytle DMX512
# fonctionne pas?

import time

print( "Running Dmx...")
nNbrChannel = 4;
dmx = DMX( num_of_channels = nNbrChannel )
print(dir(dmx))
print("INF: dmx.is_connected(): ", dmx.is_connected() )
print("INF: dmx.num_of_channels: ", dmx.num_of_channels )

print(dir(dmx.device))
print("INF: dmx.device.name: ", dmx.device.name )
print("INF: dmx.device.vid: ", dmx.device.vid ) # EUROLITE_USB_DMX512_PRO_CABLE_INTERFACE = Device(vid=1027, pid=24577)
print("INF: dmx.device.pid: ", dmx.device.pid )
print("INF: dmx.device.product: ", dmx.device.product )
print("INF: dmx.device.description: ", dmx.device.description )
print("INF: dmx.device.interface: ", dmx.device.interface )
print("INF: dmx.device.device: ", dmx.device.device )
print("INF: dmx.device.manufacturer: ", dmx.device.manufacturer )
print("INF: dmx.device.serial_number: ", dmx.device.serial_number )

print("INF: dmx: starting" )

# def set_data(self, channel_id: int, data: int, auto_send: bool = True) -> None:
"""

        :param channel_id: the channel ID as integer value between 1 and 511
        :param data: the data for the cannel ID as integer value between 0 and 255
        :param auto_send: if True, all DMX Data will be send out
        :return None:
"""

"""
assuming the first fixture is DMX channel 1 and we are in 9 channel DMX 
mode, the second fixture would need to be on channel 10, then the 3rd channel 19 and so on. 
Some DMX controllers may group fixtures in lots of 16 channels – so in that case, fixture 1 on 
11 
7
channel 1, fixture 2 on channel 17, 3 on 33, and so on. Refer to your DMX controllers’ 
instruction manual on how best to manage your DMX channel allocation. 
"""

if 0:
    print("setting all channels to 127")
    for i in range(1, nNbrChannel):
        val = 12
        print("setting channel %d to %d" % (i,val) )    
        dmx.set_data(i, val)
        dmx.send()
        time.sleep(1)
        
if 0:
    chan = 2
    print("setting channel %d to all values" % chan )
    for val in range(0,256):
        print("setting channel %d to %d" % (chan,val) )    
        dmx.set_data(chan, val)
        dmx.send()
        time.sleep(1)
        
if 0:
    chan = 2
    print("setting channel %d to all values" % chan )
    for val in range(0,256):
        print("setting channel %d to %d" % (chan,val) )    
        dmx.set_data(chan, val)
        dmx.send()
        time.sleep(1)
        

if 1:
    print("fadein-fadeout")
    dmx.set_data(1, 0)
    dmx.set_data(2, 0)
    dmx.set_data(3, 0)
    dmx.set_data(4, 0)

    time_wait = 1 # was 0.01
    while True:
        print(".")
        for i in range(0, 255, 5):
            dmx.set_data(1, i, auto_send=False)
            dmx.set_data(2, i, auto_send=False)
            dmx.set_data(3, i, auto_send=False)
            dmx.set_data(4, i)
            time.sleep(time_wait)

        for i in range(255, 0, -5):
            dmx.set_data(1, i, auto_send=False)
            dmx.set_data(2, i, auto_send=False)
            dmx.set_data(3, i, auto_send=False)
            dmx.set_data(4, i)
            time.sleep(time_wait)
