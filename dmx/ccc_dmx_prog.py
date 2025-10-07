# -*- coding: utf-8 -*-

from ccc import *

import sys
sys.path.append("../alex_pytools/")
import interpolator

"""
Alternate dmx light intensity for Oscillation

# 1. Install python
https://www.python.org/downloads/
(or brew)

# 2. Install libraries:
pip3 install serial pyserial numpy 

"Copyright" 2025 Alexandre Mazel
"""


time_prev_sec = 0

# setup pou king 40 vers cartel
# 82,162, 0, 254, 254, 254, 254, 

# king41: 
#  - a gauche du premier cartel: 208, 110
#  - premier cartel: 144, 156 ou 58, 106 (donne a peu pres le meme resultat
# - 3ieme: 156, 162
#  - dernier cartel: 240, 92 ou 160, 170 (idem)

def send_some_order( im: interpolator.InterpolatorManager, time_demo ):
    # from time to time envoyer un truc dans l'interpolateur
    global time_prev_sec
    time_sec = int(time_demo)
    if time_sec != time_prev_sec:
        time_prev_sec = time_sec
        # handle stuff for demo
        if time_sec == 1:
            print( "INF: time: %d, sending order for spot41" % time_sec )
            im.get(king_41+king_h).set( 0, 0 )
            im.get(king_41+king_v).set( 100, 0 )
            im.get(king_41+king_focus).set( 0, 0 )
            im.get(king_41+king_b).set( 255, 0 )
            im.get(king_41+king_d).set( 60, 0 )
            
        if 0:
            if time_sec == 3 and 1:
                # un balayage du 41 (center)
                duration = 2
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 50, duration )
                im.get(king_41+king_v).set( 106, duration )
                
            if time_sec == 6 and 1:
                # balayage du 41 (apres)
                duration = 2
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 63, duration )
                im.get(king_41+king_v).set( 102, duration )
                im.get(king_41+king_r).set( 255, duration )
                
                
            if time_sec == 4 and 0:
                # balayage du 41 (fin)
                duration = 5
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 75, duration )
                im.get(king_41+king_v).set( 70, duration )
                im.get(king_41+king_r).set( 255, duration )
                im.get(king_41+king_g).set( 255, 0.5, mode=mode_pingpong )
                
        if 1:
            if time_sec == 3 and 1:
                # un balayage du 41 (avant)
                duration = 2
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 144, duration )
                im.get(king_41+king_v).set( 156, duration )
                
                
            if time_sec == 6 and 1:
                # balayage du 41 (apres)
                duration = 5
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 156, duration )
                im.get(king_41+king_v).set( 162, duration )
                im.get(king_41+king_r).set( 255, duration )
                
                
            if time_sec == 11 and 1:
                # balayage du 41 (apres)
                duration = 5
                print( "INF: time: %d, sending order for spot41" % time_sec )
                im.get(king_41+king_h).set( 160, duration )
                im.get(king_41+king_v).set( 170, duration )
                im.get(king_41+king_r).set( 0, duration )
                

def prog_ccc( dm, nbr_chan ):

    im = interpolator.InterpolatorManager( nbr_chan )

    time_begin = time.time()

    # update and set values:
    #~ dmxal.set_verbose( True )

    print("looping...")
    while 1:
        
        time_demo = time.time() - time_begin

        #~ print(".")
        
        send_some_order(im, time_demo)
        
        im.update()
        for i in range( 1, nbr_chan ):
            dm.set_data(i,im.get(i).get_val())
        dm.send()
        time.sleep(0.1)
        
        if time_demo > 8 and im.is_all_finished():
            break

# prog_ccc - end

if __name__ == "__main__":
    dmx_device = None
    nbr_chan = 492+16 # how much did we use ?
    if 1:
        dmx_device = init_dmx(nbr_chan)
        dmx_device.set_optimised( True )
        dmx_device.set_clear_channel_at_exit( False )
    
    prog_ccc(dmx_device, nbr_chan)
