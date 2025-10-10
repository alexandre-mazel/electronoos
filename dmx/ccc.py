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


lustr_r = 0     # red
lustr_l = 1     # lime
lustr_a = 2     # amber
lustr_g = 3     # green
lustr_c = 4     # cyan
lustr_b = 5     # blue
lustr_i = 6      #  indigo
lustr_d = 7     # dim

# mode 16chan
king_h = 0      # horiz
king_v = 1      # vertic
king_xyspeed = 2      # 0: false, 255: flow
king_d = 3      # dim
king_r = 4      # r (then g then b)
king_g = 5
king_b = 6
king_w = 7
king_focus = 9
king_fine_h = 12
king_fine_v = 13


# mode 10chan
she_h = 0      # X: when looking to the lcd, it looks at you, then goes to the right, 83: demi tour, 170: tour complet
she_v = 1      # Y: 0: look at you, 127: vertical, 255: autre coté
she_d = 2
she_r = 3      # r (then g then b)
she_g = 4
she_b = 5

first_lustr = 1
nbr_lustr = 33
offset_lustr = 10 # nbr a multiplier entre chaque DMX

fossi_dmx = [10*offset_lustr,11*offset_lustr,12*offset_lustr,13*offset_lustr]

first_asserv = 38
nbr_asserv = 7
first_asserv_dmx = 380
offset_asserv = 16

king_38 = 380
king_40 = 412
king_41 = 428

first_she = 45
first_she_dmx = 492


def test_all_lustr( dm, first, nbr, offset, duration = 0.5 ):
    """
    - dm: the dmx controller device
    """
    print( "INF: test_all_lustr: starting" )
    all_together = 1
    for i in range( first, first+nbr ):
        print( "INF: test_all_lustr: spot %d" % i )
        if not all_together: dm.rtz()
        num_start = i * offset
        for chan in range(7):
            dm.set_data(num_start+lustr_r, (255 if chan==0 else 0) )
            dm.set_data(num_start+lustr_l, (255 if chan==1 else 0) )
            dm.set_data(num_start+lustr_a, (255 if chan==2 else 0) )
            dm.set_data(num_start+lustr_g, (255 if chan==3 else 0) )
            dm.set_data(num_start+lustr_c, (255 if chan==4 else 0) )
            dm.set_data(num_start+lustr_b, (255 if chan==5 else 0) )
            dm.set_data(num_start+lustr_i, (255 if chan==6 else 0) )
            dm.set_data(num_start+lustr_d, 40 )
            dm.send()
            if not all_together: time.sleep(duration)
            
            
def test_all_asserv( dm, first, nbr, offset, duration = 0.5 ):
    print( "INF: test_all_asserv: starting" )
    all_together = 1
    for i in range( first, first+nbr ):
        if not all_together: dm.rtz()
        num_start = (i-first) * offset + first_asserv_dmx
        print( "INF: test_all_asserv: spot %d (dmx: %d)" % (i,num_start) )
        for chan in range(3):
            dm.set_data(num_start+king_h, int(time.time()%60) ) # qu'a chaque fois il tourne un peu
            dm.set_data(num_start+king_v, 127 )
            dm.set_data(num_start+king_r, (255 if chan==0 else 0) )
            dm.set_data(num_start+king_g, (255 if chan==1 else 0) )
            dm.set_data(num_start+king_b, (255 if chan==2 else 0) )
            dm.set_data(num_start+king_d, 40 )
            dm.send()
            if not all_together: time.sleep(duration)
            
            
def test_all_she( dm, first, nbr, offset, duration = 0.5 ):
    print( "INF: test_all_she: starting" )
    all_together = 1
    for i in range( first, first+nbr ):
        if not all_together: dm.rtz()
        num_start = (i-first) * offset + first_she_dmx
        print( "INF: test_all_she: spot %d (dmx: %d)" % (i,num_start) )
        for chan in range(3):
            dm.set_data(num_start+she_h, int(time.time()%60)  ) # sint(time.time()%60) ) # qu'a chaque fois il tourne un peu
            dm.set_data(num_start+she_v, 127 )
            dm.set_data(num_start+she_r, (255 if chan==0 else 0) )
            dm.set_data(num_start+she_g, (255 if chan==1 else 0) )
            dm.set_data(num_start+she_b, (255 if chan==2 else 0) )
            dm.set_data(num_start+she_d, 40 )
            dm.send()
            if not all_together: time.sleep(duration)
            #~ exit(1)




def init_dmx( nbr_channel_to_use = 512 ):
    """
    Find the usb dmx controller and return the dmx object
    """
    
    print("INF: init_dmx: initing..." )

    dmxal.set_verbose( False )



    try:
        dmx = DMX( num_of_channels = nbr_channel_to_use )
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
        print("INF: dmx.device.serial_number: ", dmx.device.serial_number ) 
        """
        - mon truc chinois orange: BG00U0KFA
        - l'enttec de l'ensad: EN172589A
        - le noir qui clignote: BG0106SGA
        - l'enttec num4: EN495728A
        """


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
        
        
    print("INF: init_dmx: started" )
    return dmx

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

def test_ccc( dmx_device ):

    """
    syntaxe: 
    """
    

    print("Starting CCC...")
    
    dm = dmx_device
    dm.set_clear_channel_at_exit( False )
    dm.set_optimised( True )

    color = 0
    h = 0
    v = 0
    cpt = 1
    focus = 0


    dm.rtz()
    if 0:
        # eteins tout
        dm.send()
        exit(1)
    
    if 0:
        print( "Quick test chan1" )
        
        for i in range(4):
            dm.set_data(1+i,255)
        dm.send()
        time.sleep(10)
        exit()

    #~ if 1: exit() # shutdown all
    if 1: test_all_lustr( dm, first_lustr,nbr_lustr,offset_lustr)
    if 1: test_all_asserv( dm, first_asserv,nbr_asserv,offset_asserv)
    if 1: test_all_she(dm, first_she, 1, offset_asserv)
            
    if 0:
        print("sleeping")
        time.sleep(10*60)



    if 0:
        # all asserv
        while 1:
            print("color: %d" % color )
            for idx in range( first_asserv, first_asserv+nbr_asserv ):
                first_chan = (idx - first_asserv) * 16 + 380
                #~ print("first_chan:", first_chan )
                dm.set_data(first_chan+king_h, h )
                dm.set_data(first_chan+king_v, v )
                dm.set_data(first_chan+king_d, 255 ) 
                dm.set_data(first_chan+king_r+(color+0)%4, 255 ) 
                dm.set_data(first_chan+king_r+(color+1)%4, 0 )  
                dm.set_data(first_chan+king_r+(color+2)%4, 0 )  
                dm.set_data(first_chan+king_r+(color+3)%4, 0 ) 
                dm.set_data(first_chan+king_focus, focus )

            chan_lustr = 10
            dm.set_data(chan_lustr+lustr_d, 255 )
            r  = g = b = w = 0
            if color == 0:
                r = 255
            elif color == 1:
                g = 255
            elif color == 2:
                b = 255
            elif color == 3:
                w = 255
                
            if 1:
                # test rgb
                dm.set_data(chan_lustr+lustr_l, r )
                dm.set_data(chan_lustr+lustr_a, g )
                dm.set_data(chan_lustr+lustr_c, b )
            else:
                # test laci
                dm.set_data(chan_lustr+lustr_l, r )
                dm.set_data(chan_lustr+lustr_a, g )
                dm.set_data(chan_lustr+lustr_c, b )
                dm.set_data(chan_lustr+lustr_i, w )
            
            dm.send()
        
        cpt += 1
        if cpt % 10 == 0:
            color += 1
            color %= 4
        h += 2
        h %= 256
        v += 1
        v %= 256
        
        focus += 10
        focus %= 256
        
        time.sleep(0.1)
        
# test_ccc - end


if __name__ == "__main__":
    dmx_device = init_dmx()
    test_ccc(dmx_device)
    
        