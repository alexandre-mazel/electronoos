#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ccc import *

import datetime

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


# copy to Oscillation RPI:
scp ccc_dmx_prog.py na@192.168.9.102:/home/na/dev/git/electronoos/dmx/

# mettre l'heure:
sudo date -s '@1759832799'

"""

hour_demo_begin = 8 # premiere heure ou la demo commence
hour_demo_end = 24  # premiere heure ou la demo s'arrete

time_prev_sec = 0

cycle_jour = 0
cycle_fadeout = 1
cycle_nuit = 2
cycle_fadein = 3
cycle_mute = 4 # la nuit on fait rien
prev_cycle = -2

def cycle_to_lib( cycle ):
    return ["jour", "fadeout", "nuit", "fadein", "mute", "unknown"][cycle] # -1 => unknown


        
        
duration_jour = 60*5 # 60*5
duration_fadeout = 60
duration_nuit = 217
duration_fadein = 23

densite_fadeout_moitie = 50
duration_densite_fadeout_moitie = 4


if 0:
    # shorten
    duration_jour = 30+30+30+100
    duration_fadeout = 60
    duration_nuit = 60
    duration_fadein = 23

duration_loop = duration_jour + duration_fadeout + duration_nuit + duration_fadein

print("INF: duration_loop:", duration_loop )

mp = interpolator.mode_pingpong
mr = interpolator.mode_random
mper = interpolator.mode_perlin
is1 = interpolator.interpolation_sinus
is2 = interpolator.interpolation_sinus2



jour_d = 255
jour_r = 255
jour_g = 255
jour_b = 144
jour_w=255
    
"""
Nuit: 5min: dont 60s pour descendre au noir, 217s de noir, puis 23s pour remonter.
"""

nuit_d = 18
nuit_r = 0
nuit_g = 82
nuit_b = 248
nuit_w=118


# setup pou king 40 vers cartel
# 82,162, 0, 254, 254, 254, 254, 

# king41: 
#  - a gauche du premier cartel: 208, 110
#  - premier cartel: 144, 156 ou 58, 106 (donne a peu pres le meme resultat
# - 3ieme: 156, 162
#  - dernier cartel: 240, 92 ou 160, 170 (idem)

def force_nuit( im, spot, dur = 3 ):
    print("force_nuit for spot chan %d in duration %d" % (spot, dur) )
    im.get(spot+king_d).set( nuit_d, dur )
    im.get(spot+king_r).set( nuit_r, dur )
    im.get(spot+king_g).set( nuit_g, dur )
    im.get(spot+king_b).set( nuit_b, dur )
    im.get(spot+king_w).set( nuit_w, dur )

def force_jour( im, spot, dur = 3 ):
    print("force_jour for spot chan %d in duration: %d" % (spot, dur) )
    im.get(spot+king_d).set( jour_d, dur )
    im.get(spot+king_r).set( jour_r, dur )
    im.get(spot+king_g).set( jour_g, dur )
    im.get(spot+king_b).set( jour_b, dur )
    im.get(spot+king_w).set( jour_w, dur )
    
def force_penombre( im, spot, dur = duration_densite_fadeout_moitie ):
    print("force_penombre for spot chan %d in duration %d" % (spot, dur) )
    im.get(spot+king_d).set( densite_fadeout_moitie, dur )
    im.get(spot+king_r).set( nuit_r, dur )
    im.get(spot+king_g).set( nuit_g, dur )
    im.get(spot+king_b).set( nuit_b, dur )
    im.get(spot+king_w).set( nuit_w, dur )
    
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
        
def nuit_41_old(im, time_cycle ):
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

h_40_cartel = 158
v_40_cartel = 100

h_40_sol = 88
v_40_sol = 115

focus_serre_40 = 36

range_random_40_mur = 5
range_random_40_sol = 30


v_41_sol = 120

"""
29s, Panneau1: 173-3, 86, f34 tourne autour de ca 172-3 a 176-6 bas 88 a 85.
11s: Sol1: A: 188-18,118 f42, B: 202-32, 114
29s: Panneau2: 198-28, 102, f20
11s: Sol2: A: 222-52, 120, f34 B: 244-74, 106, f34
29s: Panneau3: 238-66, 92, f36
#~ 11s: Sol3: 238-68, 116, f42
30s + 11: mezzanine1 option: 201-31, 36, f68 tourner entre 198-28 36 et 204-34 38

"""

def jour_38( im, time_cycle ):
    spot = king_38
    time_1 = 29
    time_2 = 11
    time_3 = 30
    
    # loop at 150s (2.5min)
    time_cycle %= 150
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot38 (P1)" % time_cycle )
        dur = 4
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( jour_r, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
        im.get(spot+king_focus).set( 34, dur )
        im.get(spot+king_h).set( 2, dur )
        im.get(spot+king_v).set( 87, dur )
        
    if time_cycle == 6:
        im.get(spot+king_h).set( 6, 8, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( 85, 14, mode = mp, interpolation=is2 )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for jour spot38 (Sol1A)" % time_cycle )
        dur = 5
        im.get(spot+king_h).set( 18, dur )
        im.get(spot+king_v).set( 118, dur )
        im.get(spot+king_focus).set( 42, dur )
        
    if time_cycle == time_1 + 6:
        print( "INF: time: %d, sending order for jour spot38 (Sol1B)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 32, dur )
        im.get(spot+king_v).set( 114, dur )
        im.get(spot+king_focus).set( 42, dur )
        
    if time_cycle == time_1 + time_2:
        print( "INF: time: %d, sending order for jour spot38 (P2)" % time_cycle )
        dur = 3
        im.get(spot+king_h).set( 28, dur )
        im.get(spot+king_v).set( 102, dur )
        im.get(spot+king_focus).set( 20, dur )
        
    if time_cycle == time_1 + time_2 + time_1:
        print( "INF: time: %d, sending order for jour spot38 (Sol2A)" % time_cycle )
        dur = 5
        im.get(spot+king_h).set( 52, dur )
        im.get(spot+king_v).set( 120, dur )
        im.get(spot+king_focus).set( 34, dur )
        
    if time_cycle == time_1 + time_2 + time_1 + 6:
        print( "INF: time: %d, sending order for jour spot38 (Sol2B)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 74, dur )
        im.get(spot+king_v).set( 106, dur )
        
    if time_cycle == time_1 + time_2 + time_1 + time_2:
        print( "INF: time: %d, sending order for jour spot38 (P3)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 66, dur )
        im.get(spot+king_v).set( 92, dur )
        im.get(spot+king_focus).set( 36, dur )
        
    if time_cycle == time_1 + time_2 + time_1 + time_2 + time_1:
        print( "INF: time: %d, sending order for jour spot38 (S3)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 68, dur )
        im.get(spot+king_v).set( 116, dur )
        im.get(spot+king_focus).set( 42, dur )
        
    if time_cycle == time_1 + time_2 + time_1 + time_2 + time_1 + time_2:
        print( "INF: time: %d, sending order for jour spot38 (Mezza)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 28, dur )
        im.get(spot+king_v).set( 36, dur )
        im.get(spot+king_focus).set( 68, dur )
        
    if time_cycle == time_1 + time_2 + time_1 + time_2 + time_1 + time_2 + 6:
        print( "INF: time: %d, sending order for jour spot38 (Mezza)" % time_cycle )
        im.get(spot+king_h).set( 34, 8, mode = mp, interpolation=is2 )
        #~ im.get(spot+king_v).set( 85, 14, mode = mp, interpolation=is2 )
        
"""
couleur nuit: drgbw: 18, 0, 82, 248, 118
6s: pos1: 8, 104, f56?
     :pos2: 8, 128
     :pos3: 0, 128
     :pos4: 72, 102
     :pos5: 80, 74
     
    rouge a 178
"""

        
def fadeout_38( im, time_cycle ):
    spot = king_38
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for fadeout spot38 (arrivee sur zone)" % time_cycle )
        force_nuit( im, spot, 60 )
        dur = 60
        im.get(spot+king_focus).set( 56, dur//2 )
        im.get(spot+king_h).set( 8, dur )
        im.get(spot+king_v).set( 104, dur )

        
def nuit_38( im, time_cycle ):
    spot = king_38
    time_1 = 6
    
    # loop at 150s (2.5min)
    time_cycle_loop = time_cycle % 30
        
    if time_cycle_loop == time_1:
        print( "INF: time: %d, sending order for nuit spot38 (Pos2)" % time_cycle )
        dur = time_1-1
        im.get(spot+king_h).set( 8, dur )
        im.get(spot+king_v).set( 128, dur )
        
    if time_cycle_loop == time_1*2:
        print( "INF: time: %d, sending order for nuit spot38 (Pos3)" % time_cycle )
        dur = time_1-1
        im.get(spot+king_h).set( 0, dur )
        im.get(spot+king_v).set( 128, dur )
        
    if time_cycle_loop == time_1*3:
        print( "INF: time: %d, sending order for nuit spot38 (Pos4)" % time_cycle )
        dur = time_1-1
        im.get(spot+king_h).set( 72, dur )
        im.get(spot+king_v).set( 102, dur )
        
    if time_cycle_loop == time_1*4:
        print( "INF: time: %d, sending order for nuit spot38 (Pos5)" % time_cycle )
        dur = time_1-1
        im.get(spot+king_h).set( 80, dur )
        im.get(spot+king_v).set( 74, dur )

def fadein_38( im, time_cycle ):
    if time_cycle == 1:
        force_nuit( im, king_38, duration_fadein )
    nuit_38( im, time_cycle + duration_nuit )
    
"""
P1: 63, 227, f34
balaye: f96, d56 en passant par le point 84,212 et en finissant par 97, 212
P2: 105, 224, f52

rouge a 230

nuit: debut etagere: 70,216, f102

"""

def jour_39( im, time_cycle ):
    spot = king_39
    time_1 = 110 # 110
    time_2 = 20
    time_3 = 120 # 120

    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot39 (P1)" % time_cycle )
        dur = 10
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( 230, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
        im.get(spot+king_focus).set( 34, dur )
        im.get(spot+king_h).set( 63, dur )
        im.get(spot+king_v).set( 227, dur )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for jour spot39 (baisse d et f)" % time_cycle )
        dur = 4
        im.get(spot+king_focus).set( 96, dur )
        im.get(spot+king_d).set( 56, dur )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for jour spot39 (balaye centre)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 84, dur )
        im.get(spot+king_v).set( 212, dur )
        
    if time_cycle == time_1+time_2:
        print( "INF: time: %d, sending order for jour spot39 (balaye fin)" % time_cycle )
        dur = time_2-4 # pourquoi doit on enlever autant de temps juste pour qu'il ait le temps d'arriver ?
        im.get(spot+king_h).set( 97, dur )
        im.get(spot+king_v).set( 212, dur )
        
    if time_cycle == time_1+time_2*2:
        print( "INF: time: %d, sending order for jour spot39 (P2)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 105, dur )
        im.get(spot+king_v).set( 224, dur )
        # on restera fixe time_3 - 10 sec
        
    if time_cycle == time_1+time_2*2+14:
        print( "INF: time: %d, sending order for jour spot39 (a fond)" % time_cycle )
        dur = 3
        im.get(spot+king_focus).set( 52, dur )
        im.get(spot+king_d).set( 255, dur )
        # on restera fixe time_3 - 10 sec
        
    if time_cycle == time_1+time_2*2+time_3 - 8:
        print( "INF: time: %d, sending order for jour spot39 (cut)" % time_cycle )
        dur = 10
        im.get(spot+king_d).set( 0, dur )
        
    if time_cycle == time_1+time_2*2+time_3:
        print( "INF: time: %d, sending order for jour spot39 (P1 hidden)" % time_cycle )
        dur = 4
        im.get(spot+king_h).set( 63, dur )
        im.get(spot+king_v).set( 227, dur )
        
    if time_cycle == time_1+time_2*2+time_3 + 6:
        print( "INF: time: %d, sending order for jour spot39 (P1 turnon)" % time_cycle )
        dur = 5
        im.get(spot+king_d).set( 255, dur )
    
        
def fadeout_39( im, time_cycle ):
    spot = king_39
    #~ jour_39( im, time_cycle + duration_jour )
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for fadeout spot39 (fadeout)" % time_cycle )
        dur = 6
        print( "INF: time: %d, sending order for fadeout spot39 (etagere debut)" % time_cycle )
        force_penombre( im, spot )
        im.get(spot+king_h).set( 70, dur )
        im.get(spot+king_v).set( 216, dur )
        im.get(spot+king_focus).set( 102, dur )
        
    if time_cycle == 1 + duration_densite_fadeout_moitie:
        im.get(spot+king_d).set( nuit_d, duration_fadeout - duration_densite_fadeout_moitie )
        
        
def nuit_39( im, time_cycle ):
    spot = king_39
    time_1 = 6
    time_2 = 22
    time_3 = 8
    
    duration_tombe_densite_moitie = 3
    
    if time_cycle > (time_1+time_2*2+time_3):
        time_cycle =  (time_cycle-time_1)%(time_2*2+time_3) + time_1
        print("tweaked time_cycle:", time_cycle )
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for nuit spot39 (etagere debut)" % time_cycle )
        dur = time_1
        im.get(spot+king_h).set( 70, dur )
        im.get(spot+king_v).set( 216, dur )
        im.get(spot+king_focus).set( 102, dur )

    if time_cycle == time_1+2:
        print( "INF: time: %d, sending order for nuit spot39 (balaye centre)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 84, dur )
        im.get(spot+king_v).set( 212, dur )
        
    if time_cycle == time_1+time_2:
        print( "INF: time: %d, sending order for nuit spot39 (balaye fin)" % time_cycle )
        dur = time_2-4 # pourquoi doit on enlever autant de temps juste pour qu'il ait le temps d'arriver ?
        im.get(spot+king_h).set( 97, dur )
        im.get(spot+king_v).set( 212, dur )
        
    if time_cycle == time_1+time_2*2:
        dur = 4
        im.get(spot+king_d).set( 0, dur )
        
    if time_cycle == time_1+time_2*2+5:
        print( "INF: time: %d, sending order for nuit spot39 (etagere debut cache)" % time_cycle )
        dur = time_3-4
        im.get(spot+king_h).set( 70, dur )
        im.get(spot+king_v).set( 216, dur )
        im.get(spot+king_focus).set( 102, dur )
        
    if time_cycle == time_1+time_2*2+time_3-2:
        print( "INF: time: %d, sending order for nuit spot39 (remet densite)" % time_cycle )
        dur = 1
        im.get(spot+king_d).set( nuit_d, dur )

        
def fadein_39( im, time_cycle ):
    spot = king_39
    
    time_1 = 10
    time_2 = duration_fadein-time_1
    
    if time_cycle == 1:
        force_nuit( im, spot )
        dur = 5
    
        print( "INF: time: %d, sending order for fadein spot39 (etagere debut)" % time_cycle )
        im.get(spot+king_h).set( 70, dur )
        im.get(spot+king_v).set( 216, dur )
        im.get(spot+king_focus).set( 102, dur )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for fadein spot39 (P1)" % time_cycle )
        dur = time_2
        force_jour( im, spot, dur )
        im.get(spot+king_h).set( 63, dur//2 )
        im.get(spot+king_v).set( 227, dur//2 )
        im.get(spot+king_focus).set( 34, dur//2 )


def jour_40( im, time_cycle ):
    spot = king_40
    total_mur = 60 # 60
    total_cartel = 90
    total_sol = 60 # 60
    time_cartel2 = total_mur + total_cartel + total_sol
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot40 (mur)" % time_cycle )
        dur = 1
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( jour_r, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
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
        
def fadeout_40( im, time_cycle ):
    if time_cycle == 1:
        force_penombre(im, king_40)
    jour_40( im, time_cycle + duration_jour )

      
def nuit_40( im, time_cycle ):
    spot = king_40
    total_mur = 60 # 60
    if time_cycle == 1:
        print( "INF: time: %d, sending order for nuit spot40 (sol)" % time_cycle )
        dur = 1
        im.get(spot+king_d).set( nuit_d, dur )
        im.get(spot+king_r).set( nuit_r, dur )
        im.get(spot+king_g).set( nuit_g, dur )
        im.get(spot+king_b).set( nuit_b, dur )
        im.get(spot+king_w).set( nuit_w, dur )
        im.get(spot+king_focus).set( 210, dur )
        im.get(spot+king_h).set( h_40_sol, dur )
        im.get(spot+king_v).set( v_40_sol-range_random_40_sol, dur )
        
    if time_cycle == 10+2:
        im.get(spot+king_focus).set( 36, 4 )
        #~ im.get(spot+king_h).set( 128+range_random*3, 8, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( v_40_sol+range_random_40_sol, 14, mode = mp, interpolation=is2 )
        
      
def fadein_40( im, time_cycle ):
    spot = king_40
    time_1 = 10
    
    if time_cycle == 1:
        force_nuit( im, spot )
        dur = duration_fadein
    
        print( "INF: time: %d, sending order for fadein spot40 (mur1)" % time_cycle )
        im.get(spot+king_h).set( h_40_cartel, time_1 )
        im.get(spot+king_v).set( v_40_cartel, time_1 )
        
    if time_cycle == time_1:
        force_jour( im, spot, duration_fadein-time_1 )

        
"""
king41
Panneau1: 2 cartels: focus 36, cartel1: hv: 94,160, cartel2: 101, 162
Panneau2: 6 cartels: cartel1: focus 32, 138, 152, cartel2: 144, 153, c3: 150,158, 
                               c4: 152, 162, focus 30, c5: 158, 166, c6: 160,170, foc 26

aleatoire autour du sol 88, 115 pas possible, mord trop sur oscillation, 
                                        new: focus 40, 102,142 puis 120, 136,   170, 142  170, 176
aleatoire mur: entre p1c2, coin 104,160,foc68, puis fond du mur: 172,192 (alternate: capteur 164,190)

1min sol, 1min Panneau2, 1min Panneau1, 1 min mur large, 1min P2 a P1 aller/retour.

new: 
    - boucle P1, P2, Sol, idealement on commence le fadeout depuis p2-c6
    - boucle + boucle + boucle - 32
    
sol cote porte: 170,182, f26, sol cote mur: 100, 144, f26 sol transition: 156,144

"""

def jour_41( im, time_cycle ):
    spot = king_41
    
    duration_p1 = 60 # 60
    duration_p2 = 36
    duration_sol = 32
    
    
    duration_total = duration_p1 + duration_p2 + duration_sol
    
    #~ print( "INF: jour_41: duration_total:", duration_total )
    
    time_cycle %= duration_total
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot41 (P1-c1)" % time_cycle )
        force_jour(im, spot)
        dur = 3
        im.get(spot+king_focus).set( 36, dur )
        im.get(spot+king_h).set( 94, dur )
        im.get(spot+king_v).set( 160, dur )
        
    if time_cycle == 1+5:
        print( "INF: time: %d, sending order for jour spot41 (P1-c2)" % time_cycle )
        dur = 8
        im.get(spot+king_h).set( 101, dur, mode = mp, interpolation=is2 )
        im.get(spot+king_v).set( 162, dur, mode = mp, interpolation=is2 )
        
        
    if time_cycle == duration_p1:
        print( "INF: time: %d, sending order for jour spot41 (P2-c1)" % time_cycle )
        dur = 4
        im.get(spot+king_focus).set( 32, dur )
        im.get(spot+king_h).set( 138, dur )
        im.get(spot+king_v).set( 152, dur )
        
    if time_cycle == duration_p1+7:
        print( "INF: time: %d, sending order for jour spot41 (P2-c3)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 150, dur )
        im.get(spot+king_v).set( 158, dur )
        
    if time_cycle == duration_p1+19:
        print( "INF: time: %d, sending order for jour spot41 (P2-c5)" % time_cycle )
        dur = 5
        im.get(spot+king_focus).set( 26, dur )
        im.get(spot+king_h).set( 158, dur )
        im.get(spot+king_v).set( 166, dur )
        
    if time_cycle == duration_p1+29:
        print( "INF: time: %d, sending order for jour spot41 (P2-c6)" % time_cycle )
        dur = 7
        im.get(spot+king_focus).set( 26, dur )
        im.get(spot+king_h).set( 160, dur )
        im.get(spot+king_v).set( 170, dur )
        
    if time_cycle == duration_p1+duration_p2:
        print( "INF: time: %d, sending order for jour spot41 (Sol porte)" % time_cycle )
        dur = 6
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 182, dur )

    if time_cycle == duration_p1+duration_p2+10:
        print( "INF: time: %d, sending order for jour spot41 (Sol trans)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 156, dur )
        im.get(spot+king_v).set( 144, dur )        
        

    if time_cycle == duration_p1+duration_p2+22:
        print( "INF: time: %d, sending order for jour spot41 (Sol cote mur)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 144, dur )     
        
        

def fadeout_41( im, time_cycle, is_nuit = False ):
    spot = king_41

    if time_cycle == 1:
        print( "INF: time: %d, sending order for fadeout spot41 (set p2-c6)" % time_cycle )
        force_jour(im, spot, 0.5)
        dur = 2
        im.get(spot+king_focus).set( 26, dur )
        im.get(spot+king_h).set( 160, dur )
        im.get(spot+king_v).set( 170, dur )
        
    if time_cycle == 4:
        force_penombre(im, spot)
        print( "INF: time: %d, sending order for fadeout spot41 (sol porte) (is_nuit:%s)" % (time_cycle,is_nuit) )
        dur = 5
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 182, dur )
        
    if time_cycle == 4+duration_densite_fadeout_moitie+1:
        force_nuit( im, spot, duration_nuit-duration_densite_fadeout_moitie )
        

    if time_cycle == 16:
        print( "INF: time: %d, sending order for fadeout spot41 (Sol trans)" % time_cycle )
        dur = 18
        im.get(spot+king_h).set( 156, dur )
        im.get(spot+king_v).set( 144, dur )        
        

    if time_cycle == 35:
        print( "INF: time: %d, sending order for fadeout spot41 (Sol cote mur)" % time_cycle )
        dur = 22
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 144, dur )     
        
        
def nuit_41( im, time_cycle ):
    spot = king_41
    duration_total = 54
    
    change_trans = 5
    
    time_cycle %= duration_total

    if time_cycle == 1:
        print( "INF: time: %d, sending order for nuit spot41" % time_cycle )
        force_nuit(im, spot, 0.5)
        dur = 1
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 144, dur )   
        im.get(spot+king_focus).set( 40, dur )

    if time_cycle == 3:
        print( "INF: time: %d, sending order for nuit spot41 (Sol trans)" % time_cycle )
        dur = 5
        im.get(spot+king_h).set( 156, dur )
        im.get(spot+king_v).set( 144-change_trans, dur )
        
    if time_cycle == 10:
        print( "INF: time: %d, sending order for nuit spot41 (Sol trans2)" % time_cycle )
        dur = 5
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 168, dur )  
        im.get(spot+king_d).set( 0, dur )
        
    if time_cycle == 18:
        print( "INF: time: %d, sending order for nuit spot41 (Sol porte)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 170, dur )
        im.get(spot+king_v).set( 182, dur ) 
        
    if time_cycle == 18+3:
        print( "INF: time: %d, sending order for nuit spot41 (remet densite)" % time_cycle )
        im.get(spot+king_d).set( nuit_d, 3 )
        
    if time_cycle == 32:
        print( "INF: time: %d, sending order for nuit spot41 (Sol trans)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 156, dur )
        im.get(spot+king_v).set( 144-change_trans, dur )    
        
        
    if time_cycle == 40:
        print( "INF: time: %d, sending order for nuit spot41 (Sol mur)" % time_cycle )
        dur = 10
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 144-2, dur )    
        

def fadein_41( im, time_cycle ):
    spot = king_41
    
    time_1 = 6
    time_2 = duration_fadein-time_1
    
    if time_cycle == 1:
        force_nuit( im, spot )
        dur = 5
    
        print( "INF: time: %d, sending order for fadein spot41 (solmur)" % time_cycle )

        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 144-2, dur )    
        im.get(spot+king_focus).set( 50, dur//2 )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for fadein spot41 (P1-c1)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 94, dur )
        im.get(spot+king_v).set( 160, dur )
        im.get(spot+king_focus).set( 38, dur//2 )
        
    if time_cycle == time_1+10:
        print( "INF: time: %d, sending order for fadein spot41 (lumiere)" % time_cycle )
        dur = time_2-10
        force_jour( im, spot, dur )
    
        
        

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
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( jour_r, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
        im.get(spot+king_focus).set( 40, dur )
        im.get(spot+king_h).set( 152-rand, dur )
        im.get(spot+king_v).set( 162-rand, dur )
        
    if time_cycle == 4:
        im.get(spot+king_h).set( 152+rand, 4, mode = mp, interpolation=is1 )
        im.get(spot+king_v).set( 162+rand, 4, mode = mp, interpolation=is1 )
        
        
        
"""
Spot 42:
60s: P1: 84, 172, f38 puis 92,171 perlin entre les deux.
pierre: 100, 156
rotation, en v128
etagere: debut: 216, 126 fin: 217, 188

changement symetrie:
60s: P1: 168, 88, f38 puis 176, 88
pierre: 180, 104, d70
rotation: 180, 128 qui devient 128, 128 
etagere debut: 128, 134 fin: 130, 72

"""



def jour_42( im, time_cycle ):
    spot = king_42
    duration_p1 = 60 # 60
    duration_transition = 18
    duration_etagere = 32
    duration_retour = 10
    #~ total_mur = 60 # 60
    #~ total_cartel = 90
    #~ total_sol = 60 # 60
    #~ time_cartel2 = total_mur + total_cartel + total_sol
    
    margin = 2
    
    duration_total = duration_p1 + duration_transition + duration_etagere + duration_retour
    #~ print( "INF: jour_42: duration_total:", duration_total )
    
    time_cycle %= duration_total
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot42 (P1)" % time_cycle )
        force_jour(im, spot)
        dur = 3
        im.get(spot+king_focus).set( 38, dur )
        im.get(spot+king_h).set( 168-margin, dur )
        im.get(spot+king_v).set( 88, dur )
        
    if time_cycle == 7:
        print( "INF: time: %d, sending order for jour spot42 (P1-move)" % time_cycle )
        dur = 8
        im.get(spot+king_h).set( 176+margin+7, dur, mode = mp, interpolation=is2 ) # on ajoute pour mieux activer la zone
        im.get(spot+king_v).set( 88, dur, mode = mp, interpolation=is2 )
        
    if time_cycle == duration_p1:
        print( "INF: time: %d, sending order for jour spot42 (pierre)" % time_cycle )
        dur = 3
        im.get(spot+king_d).set( 70, dur+2 )
        im.get(spot+king_h).set( 180, dur )
        im.get(spot+king_v).set( 104, dur )
        
        
    if time_cycle == duration_p1+10:
        print( "INF: time: %d, sending order for jour spot42 (pierre-trans1)" % time_cycle )
        dur = 8
        im.get(spot+king_h).set( 128, dur )
        im.get(spot+king_v).set( 128, dur )
        
    #~ if time_cycle == duration_p1+6+20:
        #~ print( "INF: time: %d, sending order for jour spot42 (pierre-trans2)" % time_cycle )
        #~ dur = 3
        #~ im.get(spot+king_h).set( 200, dur )
        #~ im.get(spot+king_v).set( 128, dur )
        
    if time_cycle == duration_p1+duration_transition:
        print( "INF: time: %d, sending order for jour spot42 (etagere-debut)" % time_cycle )
        dur = 3
        im.get(spot+king_h).set( 128, dur )
        im.get(spot+king_v).set( 134, dur )
        
    if time_cycle == duration_p1+duration_transition+5:
        print( "INF: time: %d, sending order for jour spot42 (etagere-fin)" % time_cycle )
        dur = duration_etagere-3
        im.get(spot+king_focus).set( 38, dur )
        im.get(spot+king_h).set( 130, dur )
        im.get(spot+king_v).set( 72, dur )
        
    if time_cycle == duration_p1+duration_transition+duration_etagere:
        print( "INF: time: %d, sending order for jour spot42 (retour)" % time_cycle )
        dur = duration_retour-1
        im.get(spot+king_h).set( 168-margin, dur )
        im.get(spot+king_v).set( 88, dur )

"""
pareil ,mais a la place du panneau, on va sur la bruyere.
bruyere: 162 100 f38
"""
        

def fadeout_42( im, time_cycle, is_nuit = False ):
    spot = king_42
    duration_bruyere = 6 # 60
    duration_transition = 18
    duration_etagere = 32
    duration_retour = 10
    
    if is_nuit: duration_bruyere = 30
    

    if time_cycle == 1 and not is_nuit:
        print( "INF: time: %d, sending order for fadeout spot42 (set)" % time_cycle )
        force_jour(im, spot, 0.5)
        dur = 0.5
        im.get(spot+king_focus).set( 38, dur )
        im.get(spot+king_h).set( 168, dur )
        im.get(spot+king_v).set( 88, dur )
        
    if time_cycle == 3:
        force_penombre(im, spot)
        dur = duration_bruyere
        print( "INF: time: %d, sending order for fadeout spot42 (bruyere) (is_nuit:%s)" % (time_cycle,is_nuit) )
        im.get(spot+king_h).set( 162, dur )
        im.get(spot+king_v).set( 100, dur )
        
    if time_cycle == 3+duration_densite_fadeout_moitie+1:
        force_nuit( im, spot, duration_nuit-duration_densite_fadeout_moitie )

        
    if time_cycle == 3+duration_bruyere:
        print( "INF: time: %d, sending order for fadeout spot42 (pierre)" % time_cycle )
        dur = 3
        im.get(spot+king_d).set( 70, dur+2 )
        im.get(spot+king_h).set( 180, dur )
        im.get(spot+king_v).set( 104, dur )
        
        
    if time_cycle == duration_bruyere+10:
        print( "INF: time: %d, sending order for fadeout spot42 (pierre-trans1)" % time_cycle )
        dur = 8
        im.get(spot+king_h).set( 128, dur )
        im.get(spot+king_v).set( 128, dur )
        
    #~ if time_cycle == duration_p1+6+20:
        #~ print( "INF: time: %d, sending order for jour spot42 (pierre-trans2)" % time_cycle )
        #~ dur = 3
        #~ im.get(spot+king_h).set( 200, dur )
        #~ im.get(spot+king_v).set( 128, dur )
        
    if time_cycle == duration_bruyere+duration_transition:
        print( "INF: time: %d, sending order for fadeout spot42 (etagere-debut)" % time_cycle )
        dur = 3
        im.get(spot+king_h).set( 128, dur )
        im.get(spot+king_v).set( 134, dur )
        
    if time_cycle == duration_bruyere+duration_transition+5:
        print( "INF: time: %d, sending order for fadeout spot42 (etagere-fin)" % time_cycle )
        dur = duration_etagere-3
        im.get(spot+king_focus).set( 38, dur )
        im.get(spot+king_h).set( 130, dur )
        im.get(spot+king_v).set( 72, dur )
        
def nuit_42( im, time_cycle ):
    # comme fadeout
    fadeout_42( im, time_cycle, is_nuit = True )
    
def fadein_42( im, time_cycle ):
    spot = king_42
    
    time_1 = 10
    time_2 = duration_fadein-time_1
    
    if time_cycle == 1:
        force_nuit( im, spot )
        dur = 5
    
        print( "INF: time: %d, sending order for fadein spot42 (bruyere)" % time_cycle )
        im.get(spot+king_h).set( 162, dur )
        im.get(spot+king_v).set( 100, dur )
        
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for fadein spot42 (P1)" % time_cycle )
        dur = time_2
        force_jour( im, spot, dur )
        im.get(spot+king_h).set( 168, dur//2 )
        im.get(spot+king_v).set( 88, dur//2 )
        im.get(spot+king_focus).set( 38, dur//2 )
    
        
        
"""
t1: Panneau1: 79, 230, f34
01: 86,224, f56, d126
02 100,224, d62
sol1: 104, 186, f156
sol2: 64,172, f112
O3: 60,206, f66, d24
O4: 74,206, f80,d58,
"""

def jour_44( im, time_cycle ):
    spot = king_44
    time_1 = 60
    time_2 = 10
    time_3 = 13
    # (13*5+10+60)*2 = 270: on recommence la boucle pendant 30 sec sur le cartel 1
    
    # loop at 150s (2.5min)
    time_cycle %= (time_1+time_2+time_3*5)
    
    if time_cycle == 1:
        print( "INF: time: %d, sending order for jour spot44 (P1)" % time_cycle )
        dur = 10
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( jour_r, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
        im.get(spot+king_focus).set( 34, dur )
        im.get(spot+king_h).set( 79, dur )
        im.get(spot+king_v).set( 230, dur )

    if time_cycle == time_1:
        print( "INF: time: %d, sending order for jour spot44 (O1)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 86, dur )
        im.get(spot+king_v).set( 224, dur )
        im.get(spot+king_focus).set( 56, dur )
        im.get(spot+king_d).set( 126, dur )
        
    if time_cycle == time_1+time_2:
        print( "INF: time: %d, sending order for jour spot44 (O2)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 224, dur )
        im.get(spot+king_d).set( 62, dur )
        
    if time_cycle == time_1+time_2+time_3:
        print( "INF: time: %d, sending order for jour spot44 (Sol1)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 104, dur )
        im.get(spot+king_v).set( 186, dur )
        im.get(spot+king_focus).set( 156, dur )
        
    if time_cycle == time_1+time_2+time_3*2:
        print( "INF: time: %d, sending order for jour spot44 (Sol2)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 64, dur )
        im.get(spot+king_v).set( 172, dur )
        im.get(spot+king_focus).set( 112, dur )
        im.get(spot+king_d).set( 58, dur )
        
    if time_cycle == time_1+time_2+time_3*3:
        print( "INF: time: %d, sending order for jour spot44 (O3)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 60, dur )
        im.get(spot+king_v).set( 206, dur )
        im.get(spot+king_focus).set( 66, dur )
        im.get(spot+king_d).set( 24, dur )
        
    if time_cycle == time_1+time_2+time_3*4:
        print( "INF: time: %d, sending order for jour spot44 (O4)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 74, dur )
        im.get(spot+king_v).set( 206, dur )
        im.get(spot+king_focus).set( 80, dur )
        im.get(spot+king_d).set( 58, dur )
        
        
def fadeout_44( im, time_cycle ):
    if time_cycle == 1:
        force_penombre(im, king_44)
    jour_44( im, time_cycle + duration_jour )


"""
puis meme boucle, mais sans passer par le cartel panneau1 (on va ajouter un sol0)
Sol0:86, 204, f128 puis saute.

avant le fadein: on va sur P1 en gardant focus et couleur de nuit. puis pendant fadein on bouge pas.

"""

def nuit_44( im, time_cycle ):
    spot = king_44
    time_1 = 20
    time_2 = 40
    time_3 =  ( ( 300 - time_1 - time_2 )/2 // 6 )
            
    time_cycle = time_cycle % (time_1+time_2+time_3*6)
    
    duration_tombe_densite_moitie = 3
    if time_cycle == 1:
        print( "INF: time: %d, sending order for nuit spot44 (Sol1)" % time_cycle )
        dur = time_1-2
        im.get(spot+king_d).set( 128, duration_tombe_densite_moitie )
        im.get(spot+king_r).set( nuit_r, duration_fadeout )
        im.get(spot+king_g).set( nuit_g, duration_fadeout )
        im.get(spot+king_b).set( nuit_b, duration_fadeout )
        im.get(spot+king_w).set( nuit_w, duration_fadeout )
        im.get(spot+king_focus).set( 128, dur )
        im.get(spot+king_h).set( 86, dur )
        im.get(spot+king_v).set( 204, dur )
        
    if time_cycle == 1+duration_tombe_densite_moitie:
        print( "INF: time: %d, sending order for nuit spot44 (Sol1)" % time_cycle )
        im.get(spot+king_d).set( nuit_d, duration_fadeout-duration_tombe_densite_moitie )

    if time_cycle == time_1:
        print( "INF: time: %d, sending order for nuit spot44 (O2)" % time_cycle )
        dur = time_2
        im.get(spot+king_h).set( 100, dur )
        im.get(spot+king_v).set( 224, dur )
        
    if time_cycle == time_1+time_2:
        print( "INF: time: %d, sending order for nuit spot44 (Sol1)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 104, dur )
        im.get(spot+king_v).set( 186, dur )
        
    if time_cycle == time_1+time_2+time_3:
        print( "INF: time: %d, sending order for nuit spot44 (Sol2)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 64, dur )
        im.get(spot+king_v).set( 172, dur )
        
    if time_cycle == time_1+time_2+time_3*2:
        print( "INF: time: %d, sending order for nuit spot44 (O3)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 60, dur )
        im.get(spot+king_v).set( 206, dur )
        
    if time_cycle == time_1+time_2+time_3*3:
        print( "INF: time: %d, sending order for nuit spot44 (O4)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 74, dur )
        im.get(spot+king_v).set( 206, dur )
        
    if time_cycle == time_1+time_2+time_3*4:
        print( "INF: time: %d, sending order for nuit spot44 (Sol1)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 104, dur )
        im.get(spot+king_v).set( 186, dur )
        
    if time_cycle == time_1+time_2+time_3*5:
        print( "INF: time: %d, sending order for nuit spot44 (O1)" % time_cycle )
        dur = time_3
        im.get(spot+king_h).set( 86, dur )
        im.get(spot+king_v).set( 224, dur )
 
def fadein_44( im, time_cycle ):
    spot = king_44
    time_1 = 7
    if time_cycle == time_1:
        print( "INF: time: %d, sending order for fadein spot44 (P1): preparation fin de nuit" % time_cycle )
        im.get(spot+king_h).set( 79, time_1-3 )
        im.get(spot+king_v).set( 230, time_1-3 )
        
    if time_cycle == duration_fadein - time_1:
        print( "INF: time: %d, sending order for fadein spot44: debut fadein" % time_cycle )
        dur = duration_fadein - time_1
        im.get(spot+king_d).set( jour_d, dur )
        im.get(spot+king_r).set( jour_r, dur )
        im.get(spot+king_g).set( jour_g, dur )
        im.get(spot+king_b).set( jour_b, dur )
        im.get(spot+king_w).set( jour_w, dur )
        im.get(spot+king_focus).set( 34, dur )
                

def a_fond_pour_les_artistes( im ):
    print("a_fond_pour_les_artistes")
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
    
    print("first_she_dmx:", first_she_dmx )
    im.get(first_she_dmx+she_d).set( 255, dur )
    im.get(first_she_dmx+she_r).set( 255, dur )
    
    
def get_demo_times():
    """
    Return demo_time, num_cycle, time_in_cycle
    """
    
    datetimeObject = datetime.datetime.now()
    h,m,s = datetimeObject.hour, datetimeObject.minute, datetimeObject.second 
    if h < hour_demo_begin or h >= hour_demo_end:
        return 0, cycle_mute, 0
    time_demo = (h-hour_demo_begin)*60*60+m*60+s
    
    #~ time_demo *= 10 # to debug quicker

    
    time_sec = int( time_demo )
    
    time_cycle = time_sec % duration_loop

    if time_cycle <  duration_jour:
        cycle = cycle_jour
    elif time_cycle <  duration_jour+duration_fadeout:
        cycle = cycle_fadeout
        time_cycle -= duration_jour
    elif time_cycle <  duration_jour+duration_fadeout+duration_nuit:
        cycle = cycle_nuit
        time_cycle -= duration_jour+duration_fadeout
    else:
        cycle = cycle_fadein
        time_cycle -= duration_jour+duration_fadeout+duration_nuit
        
    return time_sec, cycle, time_cycle
    
          
def send_order_oscillation( im: interpolator.InterpolatorManager, time_demo: float ):
    
    global time_prev_sec, prev_cycle
    
    is_demo_time_from_start = False
    
    if is_demo_time_from_start:
        # temps depuis le lancement

        time_sec = int(time_demo)
        
        
        if time_sec == time_prev_sec:
            return        
            
        time_prev_sec = time_sec
        
        time_cycle = time_sec
        
        #~ if 1:  time_cycle += duration_jour # jump sur fadeout
        #~ if 1:  time_cycle += duration_jour+duration_fadeout # jump sur nuit
        #~ if 1:  time_cycle += duration_jour+duration_fadeout+duration_nuit # jump sur fadein
        
        time_cycle = time_cycle % duration_loop

        
        if time_cycle <  duration_jour:
            cycle = cycle_jour
        elif time_cycle <  duration_jour+duration_fadeout:
            cycle = cycle_fadeout
        elif time_cycle <  duration_jour+duration_fadeout+duration_nuit:
            cycle = cycle_nuit
        else:
            cycle = cycle_fadein
    else:
        # temps lié a l'heure
        time_sec, cycle, time_cycle = get_demo_times()
        
        if cycle == cycle_mute:
            print("muted...")
            time.sleep(1)
            return
        
        if time_sec == time_prev_sec:
            return       

        time_prev_sec = time_sec
        
    
    if prev_cycle != cycle:
        # premiere phase du cycle
        prev_cycle = cycle
        print("\n*** Premiere phase de",  cycle_to_lib(cycle) )
            
    print( "time_cycle: %s" % time_cycle )
        
    if 1:
        # autre phase du cycle
        if cycle == cycle_jour:
            pass
            jour_38( im, time_cycle )
            jour_39( im, time_cycle )
            jour_40( im, time_cycle )
            jour_41( im, time_cycle )
            jour_42( im, time_cycle)
            jour_44( im, time_cycle )
            
            
        elif cycle == cycle_fadeout:
            if is_demo_time_from_start: time_cycle -= duration_jour
            fadeout_38( im, time_cycle)
            fadeout_39( im, time_cycle)
            fadeout_40( im, time_cycle)
            fadeout_41( im, time_cycle)
            fadeout_42( im, time_cycle)
            fadeout_44( im, time_cycle)

            
        elif cycle == cycle_nuit:
            if is_demo_time_from_start: time_cycle -= duration_jour+duration_fadeout
            nuit_38( im, time_cycle )
            nuit_39( im, time_cycle )
            nuit_40( im, time_cycle )
            nuit_41( im, time_cycle )
            nuit_42( im, time_cycle )
            nuit_44( im, time_cycle )
            
        else: #  fadein
            if is_demo_time_from_start: time_cycle -= duration_jour+duration_fadeout+duration_nuit
            fadein_38( im, time_cycle )
            fadein_39( im, time_cycle )
            fadein_40( im, time_cycle )
            fadein_41( im, time_cycle)
            fadein_42( im, time_cycle)
            fadein_44( im, time_cycle)
            
                


def prog_ccc( dm, nbr_chan ):

    im = interpolator.InterpolatorManager( nbr_chan )

    time_begin = time.time()

    # update and set values:
    #~ dmxal.set_verbose( True )
    
    #~ a_fond_pour_les_ss(im)
    
    cpt = 0

    print("looping...")
    while 1:
        
        time_demo = time.time() - time_begin
        
        #~ time_demo *= 10 # to debug quicker

        #~ print(".")
        
        #~ send_some_order_test(im, time_demo)
        send_order_oscillation(im, time_demo)
        
        im.update()
        #~ print("val h: %.3f, v: %.3f" % (im.get(king_38+king_h).get_val(),im.get(king_38+king_v).get_val()) )
        #~ print("val h: %.3f, v: %.3f" % (im.get(king_39+king_h).get_val(),im.get(king_39+king_v).get_val()) )
        #~ print("val h: %.3f, v: %.3f" % (im.get(king_41+king_h).get_val(),im.get(king_41+king_v).get_val()) )
        for i in range( 1, nbr_chan ):
            val = im.get(i).get_val()
            
            if 1 and (cpt & 0) == 0 and 1:
                # lissage, using finetune
                for chan in [king_38]:
                    if i == chan+king_fine_v and 1:
                        val = im.get(chan+king_v).get_val()
                        floatingpart = val - int(val)
                        valdmx = int(floatingpart * 255)
                        #~ print("val: %s, floatingpart: %.3f, valdmx: %s" % (val,floatingpart,valdmx ) )
                        val = valdmx
                        
                    # dans les h sur le 41 ca fait trembler et c'est pas beau
                    if i == chan+king_fine_h and 1:
                        val = im.get(chan+king_h).get_val()
                        floatingpart = val - int(val)
                        valdmx = int(floatingpart * 255)
                        #~ print("val: %s, floatingpart: %.3f, valdmx: %s" % (val,floatingpart,valdmx ) )
                        val = valdmx
                        
            dm.set_data( i, int(val) )
            
        dm.send()
        
        time.sleep(0.1)
        
        cpt += 1
        
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
