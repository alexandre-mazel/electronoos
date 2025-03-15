from dmx import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
# Tested on Windows 10, amd64, Python 3.8
# Should also work on Linux, MacOS and on AARCH64 devices (ARM devices like Raspberry PI).
# Tested by Alexandre: 

# mon adaptateur:
#Veritable puce FTDI importee du Royaume-Uni. 
# Garantie de qualite 100 % garantie d'un an, entretien a vie
# Puce FT232RL + levier de vitesse RS485 avec la meilleure compatibilite et stabilite.
# Marque	Czgor?
# 20euros ttc sur Amazon
# fonctionne pas
# detecte comme FTSER2K sur port Com20 (forcage sur port 2 (pourquoi mes ports 3-19 sont réservé?par qui?)
# dans FreeStyler X2: select DMXking USB DMX512-A?

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
# avec logiciel: Freestytle DMX512

import time

print( "Running Dmx...")
nNbrChannel = 512;
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

if 0:
    print("setting all channels to 127")
    for i in range(1, nNbrChannel):
        val = 12
        print("setting channel %d to %d" % (i,val) )    
        dmx.set_data(i, val)
        dmx.send()
        time.sleep(1)
        
if 1:
    chan = 2
    print("setting channel %d to all values" % chan )
    for val in range(0,256):
        print("setting channel %d to %d" % (chan,val) )    
        dmx.set_data(chan, val)
        dmx.send()
        time.sleep(1)
        

"""
dmx.set_data(1, 0)
dmx.set_data(2, 0)
dmx.set_data(3, 0)
dmx.set_data(4, 0)

while True:
    print(".")
    for i in range(0, 255, 5):
        dmx.set_data(1, i, auto_send=False)
        dmx.set_data(2, i, auto_send=False)
        dmx.set_data(3, i, auto_send=False)
        dmx.set_data(4, i)
        time.sleep(0.01)

    for i in range(255, 0, -5):
        dmx.set_data(1, i, auto_send=False)
        dmx.set_data(2, i, auto_send=False)
        dmx.set_data(3, i, auto_send=False)
        dmx.set_data(4, i)
        time.sleep(0.01)
"""