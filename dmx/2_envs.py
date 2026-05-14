# -*- coding: utf-8 -*-

import time
import sys
from dmxal import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
import dmxal

dmxal.set_verbose( False )



nNbrChannel = 512; # le nbr que tu as prevu d'utiliser

print("INF: dmx: initing..." )

try:
    dmx1 = DMX( num_of_channels = nNbrChannel, serial_number ="EN168200A"  )
    print("INF: dmx.is_connected(): ", dmx1.is_connected() )
    print("INF: dmx.num_of_channels: ", dmx1.num_of_channels )
    print("INF: dmx.device.serial_number: ", dmx1.device.serial_number ) # mon truc chinois orange: BG00U0KFA; l'enttec de l'ensad: EN172589A, le noir qui clignote: BG0106SGA

    dmx2 = DMX( num_of_channels = nNbrChannel, serial_number ="EN172589A"  )
    print("INF: dmx.is_connected(): ", dmx2.is_connected() )
    print("INF: dmx.num_of_channels: ", dmx2.num_of_channels )
    print("INF: dmx.device.serial_number: ", dmx2.device.serial_number ) # mon truc chinois orange: BG00U0KFA; l'enttec de l'ensad: EN172589A, le noir qui clignote: BG0106SGA

except BaseException as err:
    print( "ERR: while initing enttect: err: %s" % str(err) )
    print( "ERR: you need to plus 2 enttec dmxusb pro" )
    
    
# enttec Samuel: serial_number: EN168200A
# enttec Ensad: serial_number: EN172589A


#~ dmx1.set_clear_channel_at_exit( False )

maxval = 255
minval = 0
duration = 10
dim_chan = 1

print( "dimming in %s second(s) (%.2fs per step(s))" % (duration,duration/(maxval-minval)) )
for val in range(maxval,minval,-1):
    print("dim channel %d to %d" % (dim_chan,val) )
    
    # projo qui necessite d'envoyer sur 4 chans (Brightness,R,G,B)
    
    dmx1.set_data( dim_chan, 255-val )
    dmx1.set_data( dim_chan+1, 255-val )
    dmx1.set_data( dim_chan+2, 255-val )
    dmx1.set_data( dim_chan+3, 255-val )
    dmx1.send()
    
    
    dmx2.set_data( dim_chan, val )
    dmx2.set_data( dim_chan+1, val )
    dmx2.set_data( dim_chan+2, val )
    dmx2.set_data( dim_chan+3, val )
    dmx2.send()
    time.sleep(duration/(maxval-minval))