# This one is working fine, from either web_client.html or test_client.py
import asyncio
import websockets
import time

# create handler for each connection
async def handler(websocket, path):
    try:
        while 1:
            data = await websocket.recv()
            print(dir(websocket))
            #~ addr = websocket.host
            client_ip, client_port = websocket.remote_address[:2]
            print( "DBG: handler: received from client: client_ip: %s:%s, path: %s, data: '%s'" % (str(client_ip),str(client_port), str(path),str(data) ) )
            reply = f"Data received as: {data}!"
            await websocket.send(reply)
            time.sleep(0.5)
    except websockets.exceptions.ConnectionClosedOK as err:
        print( "DBG: handler: Connection closed..." )

start_server = websockets.serve(handler, "localhost", 8000)

print( "DBG: starting server..." )
asyncio.get_event_loop().run_until_complete(start_server)

print( "DBG: running forever..." )
asyncio.get_event_loop().run_forever()