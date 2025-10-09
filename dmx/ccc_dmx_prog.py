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

cycle_jour = 0
cycle_nuit = 1
prev_cycle = -1

mp = interpolator.mode_pingpong
is1 = interpolator.interpolation_sinus
is2 = interpolator.interpolation_sinus2


# setup pou king 40 vers cartel
# 82,162, 0, 254, 254, 254, 254, 

# king41: 
#  - a gauche du premier cartel: 208, 110
#  - premier cartel: 144, 156 ou 58, 106 (donne a peu pres le meme resultat
# - 3ieme: 156, 162
#  - dernier cartel: 240, 92 ou 160, 170 (idem)

def send_orders_fossilation( im, duration, brightness, r, g, b ):
    print("INF: send_orders_fossilation" )
    mode=interpolator.mode_pingpong
    interpolation=interpolator.interpolation_sinus2
    for chan in fossi_dmx:
        im.get( chan+lustr_r ).set( r, duration, mode=mode, interpolation=interpolation )
        im.get( chan+lustr_g ).set( g, duration, mode=mode, interpolation=interpolation )
        im.get( chan+lustr_b ).set( b, duration, mode=mode, interpolation=interpolation )
        im.get( chan+lustr_d ).set( brightness, duration, mode=mode, interpolation=interpolation )

def send_some_order_test( im: interpolator.InterpolatorManager, time_demo: float ):
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
                
        if 0:
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
           
        # test she vibes
        if 0:
            if time_sec == 1 and 1:
                print( "INF: time: %d, sending order for first_she" % time_sec )
                im.get(first_she_dmx+she_h).set( 0, 0 )
                im.get(first_she_dmx+she_v).set( 0, 0 )
                im.get(first_she_dmx+she_b).set( 255, 0 )
                im.get(first_she_dmx+she_d).set( 40, 0 )
                
                
            if time_sec == 2 and 1:
                duration = 5
                print( "INF: time: %d, sending order for first_she" % time_sec )
                im.get(first_she_dmx+she_h).set( 30, duration )
                im.get(first_she_dmx+she_v).set( 20, 2, mode=interpolator.mode_pingpong, interpolation=interpolator.interpolation_sinus2 )
                
        # faire dire bonjour a tout les asserv
        if 1:
            if time_sec == 1 and 1:
                print( "INF: time: %d, sending order for all asserv!" % time_sec )
                duration = 10
                for i in range(nbr_asserv+1):
                    chan = first_asserv_dmx + offset_asserv * i
                    interpolation = interpolator.interpolation_sinus2
                    im.get(chan+king_h).set( 60, duration, mode=interpolator.mode_pingpong, interpolation=interpolation )
                    im.get(chan+king_v).set( 40, duration, mode=interpolator.mode_pingpong, interpolation=interpolation )
                    im.get(chan+king_b).set( 255, 3 )
                    im.get(chan+king_d).set( 40, 3 )
                    
            if time_sec == 1 and 1:
                send_orders_fossilation( im, 3, 255, 0, 255, 255 )
            


def jour_41old( im, time_cycle ):
    if time_cycle == 1:
        print( "INF: time: %d, sending order for spot41" % time_sec )
        duration = 1
        im.get(king_41+king_h).set( 144, duration )
        im.get(king_41+king_v).set( 156, duration )
        im.get(king_41+king_d).set( 255, duration )
        im.get(king_41+king_b).set( 255, duration )
        im.get(king_41+king_r).set( 255, duration )
        #~ im.get(king_41+king_g).set( 255, 0.5, mode=interpolator.mode_pingpong )
        im.get(king_41+king_g).set( 255, duration )
            
    if time_cycle == 3:
        print( "INF: time: %d, sending order for spot41" % time_sec )
        duration = 3
        im.get(king_41+king_h).set( 156, duration )
        im.get(king_41+king_v).set( 162, duration )
        
        
    if time_cycle == 6:
        print( "INF: time: %d, sending order for spot41" % time_sec )
        duration = 3
        im.get(king_41+king_h).set( 160, duration )
        im.get(king_41+king_v).set( 170, duration )
        
def nuit_41(im, time_cycle ):
    if time_cycle == 0:
        duration = 4
        #~ im.get(king_41+king_h).set( 160, duration )
        im.get(king_41+king_v).set( 127, duration )
        im.get(king_41+king_d).set( 30, duration )
        im.get(king_41+king_b).set( 255, duration )
    if time_cycle == 5:
        im.get(king_41+king_h).set( 140, 2.5, mode=interpolator.mode_pingpong )
        im.get(king_41+king_v).set( 147, 3.05, mode=interpolator.mode_pingpong )
        
"""
jour 5min nuit 5min
king40:

jour:
couleur: tout a fond, bleu a 144.
focus serre a 32, focus large a 118
cartel1: 158,100, et 2: 168, 102
puis va au coin 154, 98 avec focus large.
aleatoire autour du mur 128,106
aleatoire autour du sol 92, 106 - en fait h a 88 pour etre bien avec le moteur centré
1min mur, 1.5cartel, 1 sol, 1.5cartel.

nuit:
1min sol plus ouvert, 1min mur, 1 min mur2, 1 min sol
"""

h_40_mur = 128
v_40_mur = 106

h_40_sol = 88
v_40_sol = 115

focus_serre_40 = 36

range_random_40_mur = 5
range_random_40_sol = 30


v_41_sol = 120


def jour_40( im, time_cycle ):
    spot = king_40
    total_mur = 60 # 60
    total_cartel = 90
    total_sol = 60 # 60
    time_cartel2 = total_mur + total_cartel + total_sol
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot40 (mur)" % time_cycle )
        dur = 1
        im.get(spot+king_d).set( 255, dur )
        im.get(spot+king_r).set( 255, dur )
        im.get(spot+king_g).set( 255, dur )
        im.get(spot+king_b).set( 144, dur )
        im.get(spot+king_w).set( 255, dur )
        im.get(spot+king_focus).set( 200, dur )
        im.get(spot+king_h).set( h_40_mur-range_random_40_mur*3, dur )
        im.get(spot+king_v).set( v_40_mur-range_random_40_mur, dur )
        
    if time_cycle == 2:
        im.get(spot+king_h).set( h_40_mur+range_random_40_mur*3, 8, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( v_40_mur+range_random_40_mur, 14, mode = mp, interpolation=is2 )
        im.get(spot+king_focus).set( 118, 14, mode = mp, interpolation=is2 ) # en meme temps que la hauteur, on change le focus
    
    if time_cycle == total_mur or time_cycle == time_cartel2:
        print( "INF: time: %d, sending order for jour spot40 (cartel)" % time_cycle )
        dur = 10
        im.get(spot+king_focus).set( 200, dur )
        im.get(spot+king_h).set( 158, dur )
        im.get(spot+king_v).set( 100, dur )
        
    if time_cycle == total_mur+10 or time_cycle == time_cartel2+10:
        im.get(spot+king_focus).set( focus_serre_40, 5 )
        
    if time_cycle == total_mur+10+30 or time_cycle == time_cartel2+10+30:
        dur = 30
        im.get(spot+king_h).set( 168, dur )
        im.get(spot+king_v).set( 102, dur )

    if time_cycle == total_mur+total_cartel:
        print( "INF: time: %d, sending order for jour spot40 (sol)" % time_cycle )
        dur = 10
        im.get(spot+king_focus).set( 200, 2 )
        im.get(spot+king_d).set( 255, dur )
        im.get(spot+king_r).set( 255, dur )
        im.get(spot+king_g).set( 255, dur )
        im.get(spot+king_b).set( 144, dur )
        im.get(spot+king_w).set( 255, dur )
        im.get(spot+king_h).set( h_40_sol, dur )
        im.get(spot+king_v).set( v_40_sol-range_random_40_sol, dur )
        
    if time_cycle == total_mur+total_cartel+10+2:
        im.get(spot+king_focus).set( focus_serre_40, 4 )
        #~ im.get(spot+king_h).set( 128+range_random*3, 8, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( v_40_sol+range_random_40_sol, 14, mode = mp, interpolation=is2 )
      
def nuit_40( im, time_cycle ):
    spot = king_40
    total_mur = 60 # 60
    if time_cycle == 1:
        print( "INF: time: %d, sending order for nuit spot40 (sol)" % time_cycle )
        dur = 1
        im.get(spot+king_d).set( 255, dur )
        im.get(spot+king_r).set( 0, dur )
        im.get(spot+king_g).set( 0, dur )
        im.get(spot+king_b).set( 255, dur )
        im.get(spot+king_w).set( 0, dur )
        im.get(spot+king_focus).set( 200, dur )
        im.get(spot+king_h).set( h_40_sol, dur )
        im.get(spot+king_v).set( v_40_sol-range_random_40_sol, dur )
        
    if time_cycle == 10+2:
        im.get(spot+king_focus).set( 36, 4 )
        #~ im.get(spot+king_h).set( 128+range_random*3, 8, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( v_40_sol+range_random_40_sol, 14, mode = mp, interpolation=is2 )
        
      
"""
king41
Panneau1: 2 cartels: focus 36, cartel1: hv: 94,160, cartel2: 101, 162
Panneau2: 6 cartels: cartel1: focus 32, 138, 152, cartel2: 144, 153, c3: 150,158, 
                               c4: 152, 162, focus 30, c5: 158, 166, c6: 160,170, foc 26

aleatoire autour du sol 88, 115 pas possible, mord trop sur oscillation, 
                                        new: focus 40, 102,142 puis 120, 136,   170, 142  170, 176
aleatoire mur: entre p1c2, coin 104,160,foc68, puis fond du mur: 172,192 (alternate: capteur 164,190)

1min sol, 1min Panneau2, 1min Panneau1, 1 min mur large, 1min P2 a P1 aller/retour.
"""

def jour_41( im, time_cycle ):
    spot = king_41
    total_sol = 60 # 60
    total_pan2 = 60
    total_pan1 = 60
    time_mur = total_sol + total_pan2 + total_pan1
    time_p2p1 = time_mur + 60
    
    duree_pan_mur = 15 # duree entre chaque point de passage du mur
    duree_pan2_per_cartel = 12 #60/5
    #~ duree_pan2_per_cartel = 2
    
    if 1:
        # skip sol
        total_sol = 6
        duree_pan_mur = 1

    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot41 (sol)" % time_cycle )
        dur = duree_pan_mur
        im.get(spot+king_d).set( 255, dur )
        im.get(spot+king_r).set( 255, dur )
        im.get(spot+king_g).set( 255, dur )
        im.get(spot+king_b).set( 144, dur )
        im.get(spot+king_w).set( 255, dur )
        im.get(spot+king_focus).set( 40, dur )
        im.get(spot+king_h).set( 102, dur )
        im.get(spot+king_v).set( 142, dur )
        
    if time_cycle == 1+duree_pan_mur:
        dur = duree_pan_mur
        im.get(spot+king_h).set( 120, dur )
        im.get(spot+king_v).set( 136, dur )
        
    if time_cycle == 1+duree_pan_mur*2:
        dur = duree_pan_mur
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 142, dur )
        
        
    if time_cycle == 1+duree_pan_mur*3:
        dur = duree_pan_mur
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 176, dur )
        
    reduc = 0.5 #check pas de ecrasement
        
    if time_cycle == total_sol:
        print( "INF: time: %d, sending order for jour spot41 (panneau2)" % time_cycle )
        dur = 1
        im.get(spot+king_focus).set( 32, dur )
        im.get(spot+king_h).set( 138, dur )
        im.get(spot+king_v).set( 152, dur )
        #~ im.get(spot+king_xyspeed).set( 255, 1 ) # ca n'empeche pas les accoups lie au saut de 1
        
    if time_cycle == total_sol + 3 + duree_pan2_per_cartel:
        print( "INF: time: %d, sending order for jour spot41 (panneau2) - p2" % time_cycle )
        dur = duree_pan2_per_cartel-reduc
        im.get(spot+king_h).set( 144, dur )
        im.get(spot+king_v).set( 153, dur )
        
    if time_cycle == total_sol + 3 + duree_pan2_per_cartel*2:
        print( "INF: time: %d, sending order for jour spot41 (panneau2) - p3" % time_cycle )
        dur = duree_pan2_per_cartel-reduc
        im.get(spot+king_h).set( 150, dur )
        im.get(spot+king_v).set( 158, dur )
        
    if time_cycle == total_sol + 3 + duree_pan2_per_cartel*3:
        print( "INF: time: %d, sending order for jour spot41 (panneau2) - p4" % time_cycle )
        dur = duree_pan2_per_cartel-reduc
        im.get(spot+king_h).set( 152, dur )
        im.get(spot+king_v).set( 162, dur )
        im.get(spot+king_focus).set( 30, dur )
        
    if time_cycle == total_sol + 3 + duree_pan2_per_cartel*4:
        print( "INF: time: %d, sending order for jour spot41 (panneau2) - p5" % time_cycle )
        dur = duree_pan2_per_cartel-reduc
        im.get(spot+king_h).set( 158, dur )
        im.get(spot+king_v).set( 166, dur )
        
    if time_cycle == total_sol + 3 + duree_pan2_per_cartel*5:
        print( "INF: time: %d, sending order for jour spot41 (panneau2) - p6" % time_cycle )
        dur = duree_pan2_per_cartel-reduc
        im.get(spot+king_h).set( 160, dur )
        im.get(spot+king_v).set( 170, dur )
        im.get(spot+king_focus).set( 26, dur )
        
        

def jour_41_test( im, time_cycle ):
    spot = king_41
    total_sol = 60 # 60
    total_pan2 = 60
    total_pan1 = 60
    time_mur = total_sol + total_pan2 + total_pan1
    time_p2p1 = time_mur + 60


    rand = 20
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot41 (oeuvre sin)" % time_cycle )
        dur = 2
        im.get(spot+king_d).set( 255, dur )
        im.get(spot+king_r).set( 255, dur )
        im.get(spot+king_g).set( 255, dur )
        im.get(spot+king_b).set( 144, dur )
        im.get(spot+king_w).set( 255, dur )
        im.get(spot+king_focus).set( 40, dur )
        im.get(spot+king_h).set( 152-rand, dur )
        im.get(spot+king_v).set( 162-rand, dur )
        
    if time_cycle == 4:
        im.get(spot+king_h).set( 152+rand, 4, mode = mp, interpolation=is1 )
        im.get(spot+king_v).set( 162+rand, 4, mode = mp, interpolation=is1 )
        

def a_fond_pour_les_artistes( im ):
    dur = 0
    for n in range(14,33):
        chan = n*offset_lustr
        im.get(chan+lustr_d).set( 255, dur )
        im.get(chan+lustr_r).set( 255, dur )
        im.get(chan+lustr_l).set( 255, dur )
        im.get(chan+lustr_a).set( 255, dur )
        im.get(chan+lustr_g).set( 255, dur )
        im.get(chan+lustr_c).set( 255, dur )
        im.get(chan+lustr_b).set( 255, dur )
        im.get(chan+lustr_i).set( 255, dur )
                
def send_order_oscillation( im: interpolator.InterpolatorManager, time_demo: float ):
    
    global time_prev_sec, prev_cycle
    
    time_sec = int(time_demo)
    if time_sec == time_prev_sec:
        return
        
    time_prev_sec = time_sec
        
    len_cycle = 60*5
    cycle = (time_sec // len_cycle)%2
    time_cycle = time_sec % len_cycle
    
    #~ cycle += 1 #inverse jour et nuit - commence par la nuit
    
    if prev_cycle != cycle:
        # premiere phase du cycle
        prev_cycle = cycle
        if cycle == cycle_jour:
            print("jour")
        else:
            print("nuit")
            
    print( "time_cycle: %s" % time_cycle )
        
    if 1:
        # autre phase du cycle
        if cycle == cycle_jour:
            pass
            #~ jour_40( im, time_cycle )
            jour_41( im, time_cycle )
            
            
        else:
            pass
            #~ nuit_40( im, time_cycle )
            #~ nuit_41( im, time_cycle )
            
                
                

def prog_ccc( dm, nbr_chan ):

    im = interpolator.InterpolatorManager( nbr_chan )

    time_begin = time.time()

    # update and set values:
    #~ dmxal.set_verbose( True )
    
    a_fond_pour_les_artistes(im)

    print("looping...")
    while 1:
        
        time_demo = time.time() - time_begin

        #~ print(".")
        
        #~ send_some_order_test(im, time_demo)
        send_order_oscillation(im, time_demo)
        
        im.update()
        print("val h: %.3f, v: %.3f" % (im.get(king_41+king_h).get_val(),im.get(king_41+king_v).get_val()) )
        for i in range( 1, nbr_chan ):
            val = im.get(i).get_val()
            if i == king_41+king_fine_v and 0:
                val = im.get(king_41+king_v).get_val()
                floatingpart = val - int(val)
                valdmx = int(floatingpart * 255)
                #~ print("val: %s, floatingpart: %.3f, valdmx: %s" % (val,floatingpart,valdmx ) )
                val = valdmx
                
            # dans les h ca fait trembler et c'est pas beau
            if i == king_41+king_fine_h and 0:
                val = im.get(king_41+king_h).get_val()
                floatingpart = val - int(val)
                valdmx = int(floatingpart * 255)
                #~ print("val: %s, floatingpart: %.3f, valdmx: %s" % (val,floatingpart,valdmx ) )
                val = valdmx
            dm.set_data( i, int(val) )
            
        dm.send()
        time.sleep(0.1)
        
        if time_demo > 600 and im.is_all_finished():
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
