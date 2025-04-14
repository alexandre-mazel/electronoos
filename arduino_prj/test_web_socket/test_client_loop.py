import asyncio
import websockets
import time

import sys
sys.path.append("../test_socket")
from socket_server import getTimeStamp, smartFormatSize


async def msg_toggle():
    async with websockets.connect('ws://192.168.0.9:8000/ws') as websocket:
        #~ while 1:
        if 1:
            await websocket.send('toggle')
            #~ message = await websocket.read_message()
            time.sleep(0.01)
            
time_begin = time.time()
nbr_exchange = 0
nbr_received = 0
nbr_sent = 0

async def msg_loop_motor():
    global time_begin, nbr_exchange, nbr_received, nbr_sent
    async with websockets.connect('ws://192.168.0.9:8000/ws') as websocket:
        while 1:
            #~ print("DBG: Looping...")
            if 0:
                # to make the led blink
                await websocket.send('toggle')
                message = await websocket.recv() # si on met pas cette ligne, ca gele
                time.sleep(0.2) # without this line it reboots the esp32
                continue
            data = 'motor123456'
            await websocket.send( data )
            nbr_sent += len(data)
            #~ print("DBG: sent...")
            #~ message = await websocket.read_message()
            message = await websocket.recv()
            #~ print(f"Received message: {message}")
            #~ print("DBG: sleeping...")
            nbr_received += len(message)
            time.sleep(0.0001)
            
            nbr_exchange += 1
            duration = time.time() - time_begin
            if duration > 5:
                received = nbr_received / duration
                sent = nbr_sent / duration
                print( "%s: nbr_exchange: %.1f (%d), Sent: %sB, Received: %sB, Total: %sB" % ( getTimeStamp(), nbr_exchange/duration, nbr_exchange, smartFormatSize(sent), smartFormatSize(received), smartFormatSize(sent+received) ) )
                time_begin = time.time()
                nbr_exchange = 0
                nbr_received = 0
                nbr_sent = 0

#~ asyncio.get_event_loop().run_until_complete(msg_toggle())
asyncio.get_event_loop().run_until_complete(msg_loop_motor())
#~ asyncio.get_event_loop().run_forever(msg())
#~ time.sleep(3) # wait for the answer to be received (or not)