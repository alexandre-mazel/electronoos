import asyncio
import json
import random
import websockets #  sudo pip install websockets --break-system-packages

pads = {}
pad_clients = {}

def create_new_pad_id():
    while 1:
        pad_id = ""
        for i in range(4):
            pad_id += chr( ord("A") + random.randint(0,25) )
        print( "DBG: create_new_pad_id: testing new pad_id: '%s'" % pad_id )
        if pad_id not in pads:
            return pad_id
    print( "ERR: create_new_pad_id: impossible to read this message (no more combination?)" )
    return "XXXX"


async def handle_client(websocket):
    path = websocket.request.path
    query = path.split("?", 1)[1] if "?" in path else ""
    print( "DBG: handle_client: path: '%s', query: '%s'" % (path, query) )
    parameters = dict(
        item.split("=", 1)
        for item in query.split("&")
        if "=" in item
    )

    #~ pad_id = parameters.get("pad", "").upper()
    path = websocket.request.path
    pad_id = path.split("/")[2].upper()
    
    print( "DBG: handle_client: pad_id: '%s'" % (pad_id) )
    
    if( pad_id == "new_pad" ):
    {
        pad_id = create_new_pad_id()
        await websocket.send(json.dumps({
                    "type": "new_pad",
                    "pad_id": pad_id
                }))
        return
    }


    if len(pad_id) != 4 or not pad_id.isascii() or not pad_id.isalpha():
        await websocket.close(code=1008, reason="Invalid pad")
        return

    if pad_id not in pads:
        pads[pad_id] = ""

    if pad_id not in pad_clients:
        pad_clients[pad_id] = set()

    pad_clients[pad_id].add(websocket)

    await websocket.send(json.dumps({
        "type": "content",
        "content": pads[pad_id]
    }))
    
    print("DBG: initial content sent")

    try:
        async for message in websocket:
            print("DBG: received:", message)
            
            data = json.loads(message)

            if data.get("type") != "content":
                continue

            content = data.get("content", "")
            pads[pad_id] = content

            response = json.dumps({
                "type": "content",
                "content": content
            })

            clients = list(pad_clients.get(pad_id, set()))

            for client in clients:
                if client != websocket:
                    try:
                        await client.send(response)
                    except websockets.exceptions.ConnectionClosed:
                        pass

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        pad_clients[pad_id].discard(websocket)

        if not pad_clients[pad_id]:
            del pad_clients[pad_id]


port = 8765
async def run_server():
    async with websockets.serve(
        handle_client,
        "127.0.0.1",
        port
    ):
        await asyncio.Future()


def main():
    print( "INF: Running WS Server on port", port )
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
