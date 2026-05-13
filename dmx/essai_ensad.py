# -*- coding: utf-8 -*-

"""
Alternate dmx light intensity for Oscillation

# 1. Install python
https://www.python.org/downloads/
(or brew)

# 2. Install libraries:
pip3 install serial pyserial numpy 

"Copyright" 2025 Alexandre Mazel
"""

"""
ZQ02253-Moving-Head-Light
 1 000-255 Horizontal540degreescan
 2 000-255 Vertical270degreescan
 3 000-255 XYspeedfromfasttoslow
 4 000-255 Dimmingfromdarktolight
 5 000-255 Redbrightnessadjustment,fromdarktobright.
 6 000-255 Greenbrightnessadjustment,fromdarktobright.
 7 000-255 Bluebrightnessadjustment,fromdarktobright.
 8 000-255 Whitebrightnessadjustment,fromdarktobright.
 9 000-255 Strobe
 10 000-255 Focusing
 
 Autre washer:
 SHE-SWMH0718F
 DMXChannelSummary-10ChannelsMode
 Channel Value Function
 1. 0-255 X-axis,move
 2. 0-255 Y-axis,move
 3. 0-134
 135-239
 240-255
 Totaldimmer, lineardimming-DarktoBright
 Strobe,SlowtoFast
 Full light
 4. 0-255 Redlight colorcontrol, channel valueof0for theclosed
 light,1~255fortheredlightadjustment
 5. 0-255 Greencolorcontrol,channelvalueof0fortheclosedlight,
 1~255forthegreenlightadjustment
 6. 0-255 Bluelightcolorcontrol,channelvalueof0forclosedlight,
 1~255forbluelightadjustment
 7. 0-255 White light color control, thechannel valueof 0 for the
 closedlight,1~255forthebluelightadjustment
 8. 0-255 Amber light color control, thechannel valueof 0 for the
 closedlight,1~255forthebluelightadjustment
 9. 0-255 Violet light color control, thechannel valueof 0 for th
 
  10. 0-255 X/Y-axis,SlowtoFast
"""



import time
import sys
from dmxal import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
import dmxal

dmxal.set_verbose( False )



nNbrChannel = 512; # le nbr que tu as prevu d'utiliser

print("INF: dmx: initing..." )

try:
    dmx = DMX( num_of_channels = nNbrChannel )
    #~ print(dir(dmx))
    print("INF: dmx.is_connected(): ", dmx.is_connected() )
    print("INF: dmx.num_of_channels: ", dmx.num_of_channels )

    #~ print(dir(dmx.device))
    print("INF: dmx.device.name: ", dmx.device.name ) # COMx
    print("INF: dmx.device.vid: ", dmx.device.vid ) # EUROLITE_USB_DMX512_PRO_CABLE_INTERFACE = Device(vid=1027, pid=24577)
    print("INF: dmx.device.pid: ", dmx.device.pid ) # 24577
    print("INF: dmx.device.product: ", dmx.device.product ) # None
    print("INF: dmx.device.description: ", dmx.device.description ) # USB Serial Port (COMx)
    print("INF: dmx.device.interface: ", dmx.device.interface ) # None
    print("INF: dmx.device.device: ", dmx.device.device ) # COMx
    print("INF: dmx.device.manufacturer: ", dmx.device.manufacturer ) # FTDI
    print("INF: dmx.device.serial_number: ", dmx.device.serial_number ) # mon truc chinois orange: BG00U0KFA; l'enttec de l'ensad: EN172589A, le noir qui clignote: BG0106SGA

except BaseException as err:
    print("ERR: During Initing: exception: err: %s" % str(err) )
    print("Press a key to continue...")
    dummy = input()
    class FakeDmx:
        def __init__(self): pass
        def set_data( self, chan, val): pass
        def send( self): print("FakeDmx.send...")
        def set_clear_channel_at_exit(self,newval): pass
    dmx = FakeDmx()
    
    
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
Some DMX controllers may group fixtures in lots of 16 channels - so in that case, fixture 1 on 
11 
7
channel 1, fixture 2 on channel 17, 3 on 33, and so on. Refer to your DMX controllers' 
instruction manual on how best to manage your DMX channel allocation. 
"""

print("Starting Essai Ensad...")

"""
syntaxe: 
- default: send all value to all channel
- w: use a washer 16ch at dmx 200 and send graduation to 
"""

wash_id = 200

try:
    if len(sys.argv) < 2:
        # all chan change
        while 1:
            for val in [255,192,128,64]:
                print("setting all channels to %s" % val )
                for chan in range(1, nNbrChannel):
                    print("setting channel %d to value %d" % (chan,val) )   
                    dmx.set_data(chan, val)
                
                dmx.send()
                print("waiting...")
                time.sleep(5)

    elif sys.argv[1][0] == 'w' or sys.argv[1][0] == 'g':
        # all chan change but whasher in 200 in 16ch
        specific_chan = -1
        specific_val = -1
        
        if len(sys.argv) > 3:
            # change la valeur d' un chan avec une valeur specifique
            specific_chan = int( sys.argv[2] )
            specific_val = int( sys.argv[3] )
            print("Preparing to set specific channel %d to value %d" % (specific_chan,specific_val) )
            
        while 1:
            for val in [255,192,128,64]:
                for chan in range(1, wash_id):
                    print("setting channel %d to value %d" % (chan,val) )   
                    dmx.set_data(chan, val)
                    
                print("setting wash %d to %s" % (wash_id,val) )
                
                # tout a zero
                for chan in range(wash_id, wash_id+16):
                    print("setting washer channel %d to value %d" % (chan,0) )    
                    dmx.set_data(chan, 0)
                    
                # full color
                for chan in range(wash_id+4, wash_id+8):
                    print("setting washer channel %d to value %d" % (chan,255) )   
                    dmx.set_data(chan, 255)
                    
                # set dimmer
                print("setting washer intensity to value %d" % (val) ) 
                dmx.set_data(wash_id+3, val)
                
                if specific_chan != -1: 
                    print("setting specific channel %d to value %d" % (specific_chan,specific_val) )
                    dmx.set_data(specific_chan,specific_val)
                
                dmx.send()
                
                if sys.argv[1][0] != 'g':
                    print("waiting...")
                    time.sleep(5)
                else:
                    print("gradating on channel 100")
                    chan = 100
                    for val in range(0,255):
                        print("gradating channel %d to value %d" % (chan,val) )
                        dmx.set_data(chan, val)
                        dmx.send()
                        time.sleep(5/255)
    elif sys.argv[1][0] == 'f':
        print("fixed setting (blue)")
        dmx.set_data(wash_id+3, 255) # dimmer a fond
        dmx.set_data(wash_id+6, 255) # blue a fond
        dmx.set_clear_channel_at_exit( False )

        numarg = 3
        while len(sys.argv) > numarg:
            # change la valeur d' un chan avec une valeur specifique
            specific_chan = int( sys.argv[numarg-1] )
            specific_val = int( sys.argv[numarg] )
            print("+ setting to set specific channel %d to value %d" % (specific_chan,specific_val) )
            dmx.set_data(specific_chan, specific_val)      
            numarg += 2        
            
        dmx.send()
        time.sleep( 2 ) # just to be sure
        dmx.send()
        
        print( "Done" )
            
    elif sys.argv[1][0] == 'd':
        print("dim first param speed in second then specific")
        dim_chan = int( sys.argv[2] )
        
        numarg = 5
        while len(sys.argv) > numarg:
            # change la valeur d' un chan avec une valeur specifique
            specific_chan = int( sys.argv[numarg-1] )
            specific_val = int( sys.argv[numarg] )
            print("+ setting to set specific channel %d to value %d" % (specific_chan,specific_val) )
            dmx.set_data(specific_chan, specific_val)      
            numarg += 2            
            
        while 1:
            maxval = 255
            minval = 0
            if len(sys.argv) > 3:
                duration = int(sys.argv[3])
            else:
                duration = 25
            print( "dimming in %s second(s) (%.2fs per step(s))" % (duration,duration/(maxval-minval)) )
            for val in range(maxval,minval,-1):
                print("dim channel %d to %d" % (dim_chan,val) )
                dmx.set_data( dim_chan, val )
                dmx.send()
                time.sleep(duration/(maxval-minval))
            for val in range( minval,maxval ):
                print("dim channel %d to %d" % (dim_chan,val) )
                dmx.set_data( dim_chan, val )
                dmx.send()
                time.sleep(duration/(maxval-minval) )
                
                
except BaseException as err:
    print("ERR: During Running: exception: err: %s" % str(err) )
    print("Press a key to continue...")
    dummy = input()
    
print("Finished")


"""
Dimmer Botex 4 DDP-405
- Avec la ledvance 36°: 
  - Avec  le 0 ne fait pas 0.
  - On a l'impression de voir la difference que de 0 a 100.

- Ledvance 120°:
  - 20: s'allume extremement faiblement
  - 40: faible
  - 100: fort
  - moins de 150(120?): a fond

Apres redémarrage de la 36 c'est bon, elle fonctionne comme la 120.
Des fois elle repasse bizarrement dans le mode "pas eteignable".

"""