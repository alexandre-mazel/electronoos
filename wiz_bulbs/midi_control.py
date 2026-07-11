import asyncio

from pywizlight import wizlight, PilotBuilder, discovery # pip install pywizlight # NB: Requires Python version >=3.7.

import mido # pip install mido (eg 1.3.3)
import rtmidi # pip install python-rtmidi (required by mido)

import threading
import time

def print_msg( msg ):
    o = ""
    o += "hex: %s\n" % msg.hex()
    o += "is_cc: %s\n" % msg.is_cc()
    o += "channel: %s\n" % msg.channel
    if hasattr(msg, "control"):
        o += "control: %s\n" % msg.control
    o += "is_meta: %s\n" % msg.is_meta
    o += "is_realtime: %s\n" % msg.is_realtime
    o += "time: %s\n" % msg.time
    o += "type: %s\n" % msg.type
    if hasattr(msg, "value"):
        o += "value: %s\n" % msg.value
    
    print(o)
    
    
#~ hex', 'is_cc', 'is_meta', 'is_realtime', 'time', 'type', 'value']

# nuit wiz: sending, r: 3, g: 47, b: 255, ww: 0, cw: 0, mute: 0, d: 255


# print all informations from Nano Kontrol2 (works!)
r = 127
g = 127
b = 127
ww = 127 # warm white
cw = 127 # cold white
d = 127 # luminosity
mute = 0
modified = 0
time_change = time.time()

bulbs = []

async def update_lights():
    
    global modified, ww, cw, time_change, r, g, b, d, mute, bulbs
    
    bVerbose = 1
    bVerbose = 0
    
    time_last_send = time.time()
    
    if bVerbose: print( "INF: update_lights: starting...")
    
    ips_bulb = ["192.168.0.110","192.168.0.111","192.168.0.112"]
    ips_bulb = ["192.168.0.112"]
    ips_bulb = ["192.168.9.208","192.168.9.211","192.168.9.212"]
    ips_bulb = ["192.168.9.211","192.168.9.212","192.168.9.213","192.168.9.208"]
    
    for ip in ips_bulb:
        print( "INF: update_lights: connecting to %s ..." % ip )
        bulbs.append(wizlight(ip))
        
    
    while 1:
    #~ if 1:
        if bVerbose: print( "INF: update_lights: modified:", modified)
        if modified and (time.time() - time_change > 0.1 or time.time() - time_last_send > 0.5):
            modified = 0
            time_last_send = time.time()
            #~ print("sending, r: %s, g: %s, b: %s, bright: %s, mute: %s" % (r,g,b, bright, mute))
            print("sending, r: %s, g: %s, b: %s, ww: %s, cw: %s, mute: %s, d: %s" % (r,g,b, ww, cw, mute, d))
            # b  = bulbs[0]
            if 0:
                for i,bulb in enumerate(bulbs):
                    print(i)
                    if mute:
                        await bulb.turn_off()
                    else:
                        #~ await bulb.turn_on(PilotBuilder(brightness = bright,rgb = (r, g, b))
                        #~ await bulb.turn_on(PilotBuilder(rgbw = (r, g, b,bright)))
                        #~ await bulb.turn_on(PilotBuilder(rgbww = (0,0,0,113,113)))
                        await bulb.turn_on(PilotBuilder(rgbww = (r, g, b,cw,ww), brightness=d ))
            else:
                if mute:
                    results = await asyncio.gather(  *(bulb.turn_off() for bulb in bulbs), return_exceptions=True )
                else:
                    results = await asyncio.gather( *(bulb.turn_on(PilotBuilder(rgbww=(r, g, b, cw, ww), brightness=d)) for bulb in bulbs), return_exceptions=True )
                    
        #~ time.sleep(0.1)
        await asyncio.sleep(0.5)
        
def update_lights_thread():
    update_lights()
    
        
async def midi_control():
    
    global modified, ww, cw, time_change, r, g, b, d, mute, bulbs
    
    bVerbose = 1
    bVerbose = 0
    
    if 0:
        # check them
        for b in bulbs:
            print("turn on")
            #~ await b.turn_on(PilotBuilder(brightness = 255,rgb = (255, 255, 255)))
            b.turn_on(PilotBuilder(brightness = 255,rgb = (255, 255, 255)))
            time.sleep(1)
            print("turn off")
            b.turn_off()

    with mido.open_input() as inport:
        for msg in inport:
            #~ print(print_msg(msg))
            if msg.type == "note_on":
                print("note_on")
                mute = not mute
                modified = 1
                time_change = time.time()
            elif msg.type == "note_off":
                pass
            elif msg.channel >= 1:
                id = msg.channel - 1
                val = msg.value * 2+1
                if val == 1:
                    val = 0
                if bVerbose: print("id: %s, value: %s" % (id, val) )
                if id == 0:
                    r = val
                elif id == 1:
                    g = val
                elif id == 2:
                    b = val
                elif id == 3:
                    ww = val
                elif id == 4:
                    cw = val
                elif id == 5:
                    d = val
                modified = 1
                time_change = time.time()
            if bVerbose: print("loop...")
            
        print("loop2...") # never pass...
        
#~ thread_send = threading.Thread( target = update_lights_thread )

#~ thread_send.start()
#~ midi_control()


#~ loop = asyncio.get_event_loop()

#~ asyncio.run( update_lights() )

#~ loop.run_until_complete(midi_control())

#~ async def main():
    #~ # Run both tasks concurrently in the same loop
    #~ asyncio.gather(update_lights(), midi_control())

#~ asyncio.run(main())

def run_loop(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


# Start each loop in its own thread
threading.Thread(target=run_loop, args=(update_lights(),), daemon=True).start()
threading.Thread(target=run_loop, args=(midi_control(),), daemon=True).start()

# Keep main thread alive
asyncio.get_event_loop().run_forever()

