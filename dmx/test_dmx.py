# -*- coding: utf-8 -*-

from dmxal import DMX # git clone https://github.com/monzelr/dmx.git, cd dmx, pip install .
import dmxal
dmxal.set_verbose( False )

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
# 32€TTC/Amazon
# 750g
# Conso: Eteint: 2.8w(elec+fan), full RGB: 52w
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
# ch6: 0-50: open dmx, 
#         51-100: selection des couleurs du programme, 
#         101-150: jump change
#         151-200: gradual change
#         201-250: pulse change
#         251-255: voice control
# ch7: vitesse: if ch6 set to voice control: R:0-30, G:31-61, B:62:92, W:93-123&216-247, Yellow: 124-154, Pink: 155-185, Cyan: 186-215, Color Transformation: 248-255
# 
# WKL-BEAM02: R+G+B+W 12W
# 36€TTC/Amazon
# 380g
# Conso: Eteint: 3.6w(elec+fan), full W: 4.2w, full RGBW: 12.6w
# ch1: 0-8: total off (but not the fan)
#         9-134: RGBW dimmer from dark to bright
#     135-239: Strobe from slow to fast (but not fast: 6Hz-80Hz)
#     240-255: Combine ch1/ch2:ch3/ch4 et ch5 for RGBW mix
#
# ce petit spot, meme eteint relaye les commandes DMX.
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

# NE fonctionne PAS avec mon clone chinois BG00U0KFA, mais ok avec l'enttec et les projo et le dmx_tracker de Samuel

import time

def clamp(val,minval=0,maxval=255):
    if val < minval:
        return val
    if val > maxval:
        return maxval
    return val
    
def hueToRGB( hue ):
    """
    Convert a hue 0..255, to rgb 3x 0..255
    """
    r = 0 
    g = 0 
    b = 0

    hf = hue/42.5 # Not /60 as range is _not_ 0-360

    i=int( hf )
    f = hf - i
    qv = 1 - f
    tv = f

# if python 10:
    #~ match i:
        #~ case 0: 
            #~ r = 1
            #~ g = tv
            #~ break
        #~ case 1: 
            #~ r = qv;
            #~ g = 1;
            #~ break;
        #~ case 2: 
            #~ g = 1;
            #~ b = tv;
            #~ break;
        #~ case 3: 
            #~ g = qv;
            #~ b = 1;
            #~ break;
        #~ case 4:
            #~ r = tv;
            #~ b = 1;
            #~ break;
        #~ case 5: 
            #~ r = 1;
            #~ b = qv;
            #~ break;
            
    if i == 0:
            r = 1
            g = tv
    elif i == 1:
            r = qv;
            g = 1;
    elif i == 2:
            g = 1;
            b = tv;
    elif i == 3:
            g = qv;
            b = 1;
    elif i == 4:
            r = tv;
            b = 1;
    elif i == 5:
            r = 1;
            b = qv;

    ir = clamp(255*r)
    ig = clamp(255*g)
    ib = clamp(255*b)

    return ir,ig,ib
    
# clamp - end

print( "Running Dmx...")
nNbrChannel = 16; # le nbr que tu veux
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
print("INF: dmx.device.serial_number: ", dmx.device.serial_number ) # mon truc chinois: BG00U0KFA; l'enttect de l'ensad: EN172589A

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
        

if 0:
    print("fadein-fadeout device 1 a 4")
    dmx.set_data(1, 0)
    dmx.set_data(2, 0)
    dmx.set_data(3, 0)
    dmx.set_data(4, 0)

    time_wait = 0.001 # was 0.01
    while True:
        #print(".")
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
            
dev_id = 1
if 0:
    print( "fadein-fadeout device %d" % dev_id )
    time_wait = 0.001
    # regler la teinte a blanc:
    for i in range(4):
        dmx.set_data( dev_id+i, 255 )
    while True:
        print(".")
        for i in range(0, 255, 1):
            dmx.set_data( dev_id+1, i )
            time.sleep(time_wait)
        for i in range(255, 0, -1):
            dmx.set_data( dev_id+1, i )
            time.sleep(time_wait)
            
if 0:
    # fonctionne nickel!
    print( "meduse device %d" % dev_id )
    time_wait = 0.001
    # regler la teinte a blanc:
    for i in range(4):
        dmx.set_data( dev_id+i, 255 )
        
    while 1:
        for i in range(255):
            r,g,b= hueToRGB(i)
            dmx.set_data(dev_id+1,r, auto_send=False)
            dmx.set_data(dev_id+2,g, auto_send=False)
            dmx.set_data(dev_id+3,b, auto_send=True)
            time.sleep(time_wait)
            
if 0:
    print( "fade strobo device %d" % dev_id )
    time_wait = 0.1
    # regler la teinte a blanc:
    for i in range(4):
        dmx.set_data( dev_id+i, 255 )
        
    # stop strobo (so all projos are synced)
    dmx.set_data(dev_id+4,0)
    
    time.sleep(1)
        
    while 1:
        for i in range(10,255):
            dmx.set_data(dev_id+4,i)
            time.sleep(time_wait)
        for i in range(255,10,-1):
            dmx.set_data(dev_id+4,i)
            time.sleep(time_wait)
       
if 0:                 
    # ne fonctionne pas
    print( "sound react device %d" % dev_id )
    time_wait = 0.1
    # regler la teinte a blanc:
    for i in range(4):
        dmx.set_data( dev_id+i, 255 )
        
    time.sleep(1)
    
    dmx.set_data(dev_id+5,251)
    time.sleep(1)
    dmx.set_data(dev_id+6,123)
    time.sleep(1)
    
if 1:
    print("midi controlled device 1 a 4 (4 slider of the noanokontrol2)")
    # command by midi
    import mido # pip install mido (eg 1.3.3)
    import rtmidi # pip install python-rtmidi (required by mido)


    # print all informations from Nano Kontrol2 (works!)
    with mido.open_input() as inport:
        for msg in inport:
            if msg.channel >= 1:
                id = dev_id+msg.channel - 1
                val = msg.value * 2+1
                print("id: %s, value: %s" % (id, val) )
                dmx.set_data( id,val )

    