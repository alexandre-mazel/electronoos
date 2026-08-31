import asyncio
import json
import websockets

pads = {}
pad_clients = {}


async def handle_client(websocket):
    path = websocket.request.path
    query = path.split("?", 1)[1] if "?" in path else ""
    parameters = dict(
        item.split("=", 1)
        for item in query.split("&")
        if "=" in item
    )

    pad_id = parameters.get("pad", "").upper()

    if len(pad_id) != 4 or not pad_id.isalpha():
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

    try:
        async for message in websocket:
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


async def run_server():
    async with websockets.serve(
        handle_client,
        "127.0.0.1",
        8765
    ):
        await asyncio.Future()


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
