from microbit import *
import time

def get_current_time():
    "Return time in sec"
    return running_time() // 1000

def smart_string( sec ):
    if sec > 60:
        return str(sec//60)
    return str(sec)

def wait_time( timer_duration = 25*60):
    time_begin = get_current_time()
    
    
    prev_msg = ""
    while 1:
        remain = timer_duration - (get_current_time() - time_begin)
        msg = smart_string(remain)
        print("remain:", remain, ", smart_string:", msg )
        if msg != prev_msg:
            if len(msg) > 1:
                display.scroll( msg, wait=False, loop=True, delay = 100 )
            else:
                display.show( msg, wait=False )
            prev_msg = msg
    
        if remain < 1 or button_b.was_pressed():
            global mode
            mode = (mode + 1) % 2
            return;
            
        if button_a.was_pressed():
            return
        sleep(1000)

mode = 0 # 0: pomodoro, 1: juste 2 minutes pour du gainage
while 1:
    minute_to_sec = 60
    #minute_to_sec = 1 # to test quickly
    if mode == 0:
        wait_time( 25 * minute_to_sec )
        audio.play(Sound.YAWN)
        if mode == 0:
            wait_time( 5 * minute_to_sec )
            audio.play(Sound.GIGGLE)
    else:
        wait_time( 2 * minute_to_sec )
        audio.play(Sound.YAWN)
        