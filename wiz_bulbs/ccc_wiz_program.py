# -*- coding: utf-8 -*-

import asyncio
import time

import fade_wiz
from fade_wiz import col_blue, col_green, col_red, col_off, col_full, fade_all_wiz

import sys
sys.path.append( "../dmx" )

import ccc_dmx_prog
from ccc_dmx_prog import duration_jour, duration_fadeout, duration_nuit, duration_fadein, get_demo_times, cycle_jour, cycle_nuit, cycle_fadeout, cycle_jour, cycle_fadein, cycle_mute, cycle_to_lib


def get_all_ips():
    print( "get_all_ips..." )
    ips_bulb = ["192.168.0.111","192.168.0.113","192.168.0.116"]
    return ips_bulb
    
    
    
col_jour = (0,0,0,255,255,255)
col_nuit = (0, 5, 30,0,0,40)
    
    
    
time_prev_sec = -2
prev_cycle = -2

time_last_check_ip = time.time()
    
def run_demo():
    global time_prev_sec, prev_cycle, time_last_check_ip
    
    ips_bulb = get_all_ips()
    loop = asyncio.get_event_loop()
    
    is_first_time = True
    
    while 1:

        # temps lié a l'heure
        time_sec, cycle, time_cycle = get_demo_times()
        
        if cycle == cycle_mute:
            print("muted...")
            time.sleep(1)
            continue
        
        if time_sec == time_prev_sec:
            time.sleep( 0.1 )
            continue
            
        time_retry_ip = 20*60
        time_retry_ip = 20 # to check in demo
        if time.time() - time_last_check_ip > time_retry_ip:
            time_last_check_ip = time.time()
            print( "Recreating IPs" )
            ips_bulb = get_all_ips() # reprend toutes les ips et essaye de se reconnecter a des nouvelles lampes qui serait arriver entre temps

        time_prev_sec = time_sec
        
        
        if prev_cycle != cycle:
            # premiere phase du cycle
            prev_cycle = cycle
            print("\n*** Premiere phase de",  cycle_to_lib(cycle) )
            
            if cycle == cycle_jour:
                pass
            if cycle == cycle_fadeout or ( is_first_time and cycle == cycle_nuit ):
                loop.run_until_complete(fade_all_wiz(col_jour,col_nuit,duration_fadeout,ips_bulb=ips_bulb))
            if cycle == cycle_nuit:
                pass
            if cycle == cycle_fadein or ( is_first_time and cycle == cycle_jour ):
                loop.run_until_complete(fade_all_wiz(col_nuit,col_jour,duration_fadein,ips_bulb=ips_bulb))
        else:
            # autre phase du cycle
            pass
            
            
        is_first_time = False
        time.sleep( 0.1 )
        
        
if __name__ == "__main__":
    run_demo()
    
    

