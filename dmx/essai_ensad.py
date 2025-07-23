# -*- coding: utf-8 -*-

import time
from dmxal import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
import dmxal
dmxal.set_verbose( False )



nNbrChannel = 256; # le nbr que tu veux

print("INF: dmx: initing..." )

if 1:
    dmx = DMX( num_of_channels = nNbrChannel )
    print(dir(dmx))
    print("INF: dmx.is_connected(): ", dmx.is_connected() )
    print("INF: dmx.num_of_channels: ", dmx.num_of_channels )

    print(dir(dmx.device))
    print("INF: dmx.device.name: ", dmx.device.name ) # COMx
    print("INF: dmx.device.vid: ", dmx.device.vid ) # EUROLITE_USB_DMX512_PRO_CABLE_INTERFACE = Device(vid=1027, pid=24577)
    print("INF: dmx.device.pid: ", dmx.device.pid ) # 24577
    print("INF: dmx.device.product: ", dmx.device.product ) # None
    print("INF: dmx.device.description: ", dmx.device.description ) # USB Serial Port (COMx)
    print("INF: dmx.device.interface: ", dmx.device.interface ) # None
    print("INF: dmx.device.device: ", dmx.device.device ) # COMx
    print("INF: dmx.device.manufacturer: ", dmx.device.manufacturer ) # FTDI
    print("INF: dmx.device.serial_number: ", dmx.device.serial_number ) # mon truc chinois orange: BG00U0KFA; l'enttec de l'ensad: EN172589A, le noir qui clignote: BG0106SGA

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

print("Starting Essai Ensad")

if 1:
    while 1:
        for val in [255,192,128,64]:
            print("setting all channels to %s" % val )
            for chan in range(1, nNbrChannel):
                print("setting channel %d to value %d" % (chan,val) )    
                dmx.set_data(chan, val)
                dmx.send()
            print("waiting...")
            time.sleep(5)
        

    

    