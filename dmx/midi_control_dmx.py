
from ccc import *
import mido # pip install mido (eg 1.3.3)
import rtmidi # pip install python-rtmidi (required by mido)

def a_fond_pour_les_artistes( dm ):
    dur = 0
    for n in range(14,33):
        chan = n*offset_lustr
        dm.set_data(chan+lustr_d, 255 )
        dm.set_data(chan+lustr_r, 255 )
        dm.set_data(chan+lustr_l, 255 )
        dm.set_data(chan+lustr_a, 255 )
        dm.set_data(chan+lustr_g, 255 )
        dm.set_data(chan+lustr_c, 255 )
        dm.set_data(chan+lustr_b, 255 )
        dm.set_data(chan+lustr_i, 255 )
    dm.send()

if __name__ == "__main__":
    dmx_device = None
    nbr_chan = 492+16 # how much did we use ?
    if 1:
        dmx_device = init_dmx(nbr_chan)
        dmx_device.set_optimised( True )
        dmx_device.set_clear_channel_at_exit( False )


 # cf https://mido.readthedocs.io/en/stable/

#~ print(dir(mido))

dm = dmx_device

#~ a_fond_pour_les_artistes( dm )

chan = king_38
chan = king_39
chan = king_40
chan = king_41
chan = king_42
#~ chan = king_43
#~ chan = king_44


# pour chaque tranche, comment tomber sur la commande qui correspond au prog du spot.
# on veut: luminosite,  R G B,  col extra, col extra2, col extra3, X et Y.
option = king_xyspeed
option = king_fine_h
conv_king =  [king_d,  king_r, king_g, king_b, king_w,  king_focus, option,  king_h, king_v]
conv_spot = conv_king

# print all informations from Nano Kontrol2 (works!)
with mido.open_input() as inport:
    for msg in inport:
        #~ print(msg)
        cmd = msg.channel
        if hasattr(msg,"note"):
            if msg.note == 45:
                if msg.velocity == 127:
                    print("recorded: ")
                    for i in range( 16 ):
                        print( "%d, " % dm.get_data( chan+i ), end = "" )
                    print( "" )
                continue
        if msg.control == 16:
            cmd = 0
        val = msg.value*2
        cmd_conv = conv_spot[cmd]
        print("chan:%d, send: %d, conv %d: val: %d" % (chan+cmd_conv, cmd,cmd_conv, val) )
        dm.set_data( chan+cmd_conv, val )
        dm.send()
        
        
        