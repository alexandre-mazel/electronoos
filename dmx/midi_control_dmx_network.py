import asyncio

import mido # pip install mido (eg 1.3.3)
import rtmidi # pip install python-rtmidi (required by mido)

import threading
import time
import socket


"""
Couleur pour phospho en nuit: indigo3, d:255
fossilation: 89, 21, 157, 0, 0, 0,0,123 - basse: d77, haute: 165
fossilation nuit: 0, 0, 169, 0, 0, 149, 33, 207, basse: d105, haute: 175
new nuit:          0, 0, 83, 0, 0, 255, 35, 161, meme ecart

lavande (mode nuit): 9, 47, 0, 0, 73, 171, 255, 105

"""

r = 127
l = 127
a = 127
g = 127
c = 127
b = 127
i = 127
d = 127
mute = 0
modified = 0
time_change = time.time()

async def midi_control():
    
    global modified, ww, cw, time_change, r, l, a, g, c, b, i, d, mute, bulbs
    
    bVerbose = 1
    bVerbose = 0


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
                    l = val
                elif id == 2:
                    a = val
                elif id == 3:
                    g = val
                elif id == 4:
                    c = val
                elif id == 5:
                    b = val
                elif id == 6:
                    i = val
                elif id == 7:
                    d = val    
                    
                modified = 1
                time_change = time.time()
            if bVerbose: print("loop...")
            
        print("loop2...") # never pass...
        

def run_loop(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    
threading.Thread(target=run_loop, args=(midi_control(),), daemon=True).start()

def send_values(host="127.0.0.1", port=9000, chan = 80, values=(421)):
    
    bVerbose = 1
    #~ bVerbose = 0
    
    dur = 0.1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if 0:
            # un msg par commande
            for i,v in enumerate(values):
                msg = str((chan+i,v,dur)) +'|' # on met | pour marquer la fin
                msg = msg.encode()
                s.sendall(msg + b"\n")
                if bVerbose: print(f"Sent: {msg}")
        else:
            # un msg pour toutes les commandes:
            msg = ""
            for i,v in enumerate(values):
                msg += str((chan+i,v,dur)) +'|'
            msg = msg.encode()
            s.sendall(msg + b"\n")
            if bVerbose: print(f"Sent: {msg}")

host = "192.168.9.110"
while 1:
    if modified:
        modified = 0
        values = (r,l,a,g,c,b,i,d)
        print("values:", values )
        if 0:
            # fossilation
            send_values(host=host,values=values, chan=100)
            send_values(host=host,values=values, chan=110)
            send_values(host=host,values=values, chan=120)
            send_values(host=host,values=values, chan=130)
        else:
            send_values(host=host,values=values, chan=180)
        
    time.sleep(0.4)
        