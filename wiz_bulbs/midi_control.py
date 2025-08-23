import asyncio

from pywizlight import wizlight, PilotBuilder, discovery # pip install pywizlight # NB: Requires Python version >=3.7.

import mido # pip install mido (eg 1.3.3)
import rtmidi # pip install python-rtmidi (required by mido)

import time

def print_msg( msg ):
    o = ""
    o += "hex: %s\n" % msg.hex()
    o += "is_cc: %s\n" % msg.is_cc()
    o += "channel: %s\n" % msg.channel
    o += "control: %s\n" % msg.control
    o += "is_meta: %s\n" % msg.is_meta
    o += "is_realtime: %s\n" % msg.is_realtime
    o += "time: %s\n" % msg.time
    o += "type: %s\n" % msg.type
    o += "value: %s\n" % msg.value
    
    print(o)
    
    
#~ hex', 'is_cc', 'is_meta', 'is_realtime', 'time', 'type', 'value']


# print all informations from Nano Kontrol2 (works!)
r = 127
g = 127
b = 127
bright = 255
modified = 1
time_change = time.time()

async def update_lights():
    
    while 1:
        if modified and time.time() - time_change > 0.1:
            modified = 0
            print("sending...")
            await bulbs[0].turn_on(PilotBuilder(brightness = bright,rgb = (r, g, b)))
        time.sleep(0.1)
    
        
async def midi_control():
    
    ips_bulb = ["192.168.0.110","192.168.0.111","192.168.0.112"]
    
    bulbs = []
    
    for ip in ips_bulb:
        print( "INF: midi_control: connecting to %s ..." % ip )
        bulbs.append(wizlight(ip))
        
    if 0:
        # check them
        for b in bulbs:
            print("turn on")
            await b.turn_on(PilotBuilder(brightness = 255,rgb = (255, 255, 255)))
            time.sleep(1)
            print("turn off")
            await b.turn_off()

    with mido.open_input() as inport:
        for msg in inport:
            #~ print(print_msg(msg))
            if msg.channel >= 1:
                id = msg.channel - 1
                val = msg.value * 2+1
                print("id: %s, value: %s" % (id, val) )
                if id == 3:
                    r = val
                elif id == 4:
                    g = val
                elif id == 5:
                    b = val
                elif id == 6:
                    bright = val
                modified = 1
                time_change = time.time()
            print("loop...")
            
        print("loop2...") # never pass...
        
loop = asyncio.get_event_loop()
loop.run_until_complete(midi_control())