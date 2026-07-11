import asyncio
import websockets
import time


async def msg():
    async with websockets.connect('ws://localhost:8000') as websocket:
        await websocket.send('test message')

asyncio.get_event_loop().run_until_complete(msg())
#~ time.sleep(3) # wait for the answer to be received (or not)