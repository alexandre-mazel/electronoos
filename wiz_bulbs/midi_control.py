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
modified = 0
time_change = time.time()

bulbs = []

async def update_lights():
    
    global modified, bright, time_change, r, g, b, bulbs
    
    time_last_send = time.time()
    
    print( "INF: update_lights: starting...")
    
    ips_bulb = ["192.168.0.110","192.168.0.111","192.168.0.112"]
    
    for ip in ips_bulb:
        print( "INF: update_lights: connecting to %s ..." % ip )
        bulbs.append(wizlight(ip))
        
    
    while 1:
    #~ if 1:
        print( "INF: update_lights: modified:", modified)
        if modified and (time.time() - time_change > 0.1 or time.time() - time_last_send > 0.5):
            modified = 0
            time_last_send = time.time()
            print("sending, r: %s, g: %s, b: %s" % (r,g,b))
            # b  = bulbs[0]
            for bulb in bulbs:
                await bulb.turn_on(PilotBuilder(brightness = bright,rgb = (r, g, b)))
        #~ time.sleep(0.1)
        await asyncio.sleep(0.1)
        
def update_lights_thread():
    update_lights()
    
        
async def midi_control():
    
    global modified, bright, time_change, r, g, b, bulbs
    
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

