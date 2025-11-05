#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import datetime
import os
import time

import fade_wiz
from fade_wiz import col_blue, col_green, col_red, col_off, col_full, fade_all_wiz

import sys
sys.path.append( "../dmx" )

import ccc_dmx_prog
from ccc_dmx_prog import duration_jour, duration_fadeout, duration_nuit, duration_fadein, get_demo_times, cycle_jour, cycle_nuit, cycle_fadeout, cycle_jour, cycle_fadein, cycle_mute, cycle_to_lib


def get_all_ips():
    print( "get_all_ips..." )
    if 1:
        # alex house
        ips_bulb = ["192.168.0.111","192.168.0.113","192.168.0.116"]
        
    ips_bulb_rail1 = ["192.168.9.201","192.168.9.202","192.168.9.203","192.168.9.204","192.168.9.205","192.168.9.206","192.168.9.207"]
    ips_bulb_rail2 = ["192.168.9.208","192.168.9.209","192.168.9.210","192.168.9.211","192.168.9.212","192.168.9.213","192.168.9.215","192.168.9.216","192.168.9.217"]
    ips_bulb_rail3 = ["192.168.9.218","192.168.9.219","192.168.9.220","192.168.9.221"]
    ips_bulb_ccc_spare = ["192.168.9.225","192.168.9.226","192.168.9.227"]
    
    ips_bulb_rail_sans_vert = ["192.168.9.208","192.168.9.211","192.168.9.212","192.168.9.213"]
    
    if 1:
        ips_bulb = []
        ips_bulb.extend( ips_bulb_rail1 )
        ips_bulb.extend( ips_bulb_rail2 )
        ips_bulb.extend( ips_bulb_rail3 )
        
        #~ ips_bulb = ips_bulb_rail_sans_vert
        
        
    #~ ips_bulb = ips_bulb_ccc_spare # debug et timing chez moi avec le tp_link wifi7: 0.11 par appel

    return ips_bulb
    
    
def getTimeStamp():
    """
    
    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp
    
def log( msg ):
    if os.name == "nt": return
    fn = "/home/pi/logs/ccc_wiz_program.log"
    fn = open(fn,"at")
    fn.write( getTimeStamp() + ": " + msg + "\n" )
    fn.close()
    
    
    
col_jour = (0,0,0,255,255,255)
col_nuit = (0, 5, 30,0,0,40)
col_nuit = (3, 47, 255,0,0,255)
col_nuit_sans_vert = (3, 0, 255,0,0,255)
    
    
    
time_prev_sec = -2
prev_cycle = -2

time_last_check_ip = time.time()
    
def run_demo():
    global time_prev_sec, prev_cycle, time_last_check_ip
    
    ips_bulb = get_all_ips()
    loop = asyncio.get_event_loop()
    
    is_first_time = True
    
    while 1:

        # temps lie a l'heure
        time_sec, cycle, time_cycle = get_demo_times()
        
        # debug
        #~ cycle = cycle_jour
        #~ cycle = cycle_nuit
        #~ cycle = cycle_mute
        
        #~ if cycle == cycle_mute:
            #~ print("muted...")
            #~ time.sleep(1)
            #~ continue
        
        if time_sec == time_prev_sec:
            time.sleep( 0.1 )
            continue
            
        time_retry_ip = 20*60
        #~ time_retry_ip = 20 # to check quickly in test mode
        time_retry_ip = 2 * 60
        
        if 0 or ( cycle != cycle_mute and time.time() - time_last_check_ip > time_retry_ip and len(ips_bulb) < 17):
            time_last_check_ip = time.time()
            print( "Recreating IPs" )
            log("Recreating IP, len: %d, list: %s" % (len(ips_bulb),ips_bulb) )
            ips_bulb = get_all_ips() # reprend toutes les ips et essaye de se reconnecter a des nouvelles lampes qui serait arriver entre temps

        time_prev_sec = time_sec
        
        
        if prev_cycle != cycle:
            # premiere phase du cycle
            prev_cycle = cycle
            print("\n*** Premiere phase de",  cycle_to_lib(cycle) )

            if cycle == cycle_mute:
                loop.run_until_complete(fade_all_wiz(col_nuit,col_off,10,ips_bulb=ips_bulb))
                loop.run_until_complete(fade_all_wiz(col_off,col_off,2,ips_bulb=ips_bulb))
                
            if cycle == cycle_jour:
                pass
            if cycle == cycle_fadeout or ( is_first_time and cycle == cycle_nuit ):
                loop.run_until_complete(fade_all_wiz(col_jour,col_nuit,duration_fadeout-1,ips_bulb=ips_bulb))
            if cycle == cycle_nuit:
                pass
            if cycle == cycle_fadein or ( is_first_time and cycle == cycle_jour ):
                loop.run_until_complete(fade_all_wiz(col_nuit,col_jour,duration_fadein-1,ips_bulb=ips_bulb))
        else:
            # autre phase du cycle
            pass
            
            
        is_first_time = False
        time.sleep( 0.1 )
        
        
if __name__ == "__main__":
    # on la relance si elle plante sur une erreur inconnue
    log("started...")
    while 1:
        try:
                run_demo()
        except BaseException as err:
            s = "ERR: unknown exception 421: ", str(err)
            print( s )
            log(s)
            time.sleep( 30 )
    

