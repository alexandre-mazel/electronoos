import asyncio
import json
import os
import random
import re
import time
import websockets #  sudo pip install websockets --break-system-packages

pads = {}
pad_clients = {}

save_path = "./apads/"

info_ip = {}

def retrieve_info_on_ip( ip ):
    import requests

    print("INF: retrieve_info_on_ip: ip:", str(ip) )

    try:
        received_data = requests.get( f"https://ipinfo.io/{ip}/json", timeout=10 )
        print("INF: retrieve_info_on_ip: received_data:", str(received_data) )
        
        data = received_data.json()
        
        print("INF: retrieve_info_on_ip: data:", str(data) )
    except BaseException as err:
        print("ERR: retrieve_info_on_ip:", str(err) )
        return ""
    
    org = data.get("org", "").lower()
    print("INF: retrieve_info_on_ip: org:", str(org) )

    if "orange" in org:
        operator = "orange"
    elif "free" in org or "proxad" in org:
        operator = "free"
    elif "sfr" in org or "ldcom" in org:
        operator = "sfr"
    else:
        operator = org # "unknown"
       
    postal = data.get("postal", "")
    if  postal != "":
        operator += " - " + postal
        
    loc = data.get("loc", "")
    if  loc != "":
        operator += " - " + loc
        
    print("INF: retrieve_info_on_ip: operator:", str(operator) )
        
    return operator



def get_info_on_ip( ip ):
    global info_ip
    
    if ip.startswith( "192.168."):
        return ""
    if ip in info_ip: return info_ip[ip]
    info = retrieve_info_on_ip( ip )
    info_ip[ip] = info
    
    

def create_new_pad_id():
    # ici que avec des lettres
    while 1:
        pad_id = ""
        for i in range(4):
            pad_id += chr( ord("A") + random.randint(0,25) )
        print( "DBG: create_new_pad_id: testing new pad_id: '%s'" % pad_id )
        if pad_id not in pads:
            return pad_id
    print( "ERR: create_new_pad_id: impossible to read this message (no more combination?)" )
    return "XXXX"
    
def save_on_disk( pad_id ):
    contents = pads[pad_id]
    fn = save_path + str(pad_id) + ".txt"
    if os.path.exists( fn ) and os.path.getsize( fn ) > len( contents ):
        # backup car plus petit
        fn_backup = fn.replace( ".txt", "_%012d.txt" % int(time.time()*100) )
        print("INF: save_on_disk: moving '%s' to '%s'" % (fn,fn_backup) )
        os.rename( fn, fn_backup )
    f = open( fn, "wt", encoding="utf-8" )
    f.write( contents )
    f.close()
    
def load_from_disk( pad_id, default_contents = "" ):
    fn = save_path + str(pad_id) + ".txt"
    if not os.path.exists( fn ):
        return default_contents
    f = open( fn, "rt", encoding="utf-8" )
    if f == None:
        return default_contents
    contents = f.read()
    f.close()
    return contents


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


    #~ if len(pad_id) != 4 or not pad_id.isascii() or not pad_id.isalpha(): # check only 4 chars (en fait jusqu'a 8 c'est plus pratique pour d'autres prenoms ou une sorte d'obfuscation)
    if len(pad_id) > 8 or not re.match(r'^[A-Z0-9]{1,8}$', pad_id): 
        await websocket.close(code=1008, reason="Invalid pad")
        return

    if pad_id not in pads:
        pads[pad_id] = load_from_disk( pad_id, "" )

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
            print("DBG: received:", message )
            

            ip, port = websocket.remote_address
            print( "Client:", ip, "port:", port )
            
            headers = websocket.request.headers

            strForwardedFor = headers.get("X-Forwarded-For")
            strRealIP = headers.get("X-Real-IP")
            print("X-Forwarded-For:", strForwardedFor )
            print("X-Real-IP:", strRealIP)
            
            if strForwardedFor != "" and strForwardedFor != None:
                ip = strForwardedFor
                
            if strRealIP != "" and strRealIP != None:
                ip = strRealIP
            
            print( "Finally: Client:", ip, "port:", port )
            
            # pour rigoler on check les ip
            #~ if ip.startswith( "92.184.140" ):
                #~ ip += " (orange)"
            info = get_info_on_ip( ip )
            if info != "" and info != None:
                ip += " (%s)" % info
            
            data = json.loads(message)

            if data.get("type") == "new_pad":
                pad_id = create_new_pad_id()
                pads[pad_id] = load_from_disk( pad_id, "" )
                pad_clients[pad_id] = set()

                await websocket.send(json.dumps({
                    "type": "new_pad",
                    "pad_id": pad_id
                }))

                continue

            content = data.get("content", "")
            pads[pad_id] = content
            save_on_disk( pad_id )

            response = json.dumps({
                "type": "content",
                "content": content,
                "author": str(ip)
            })

            clients = list(pad_clients.get(pad_id, set()))
            
            print(
                f"DBG: BROADCAST: {len(clients)} clients, "
                f"sender={websocket.remote_address}, "
                f"response={response!r}",
                flush=True,
        )


            for client in clients:
                if client != websocket:
                    try:
                        print(
                            f"DBG: broadcasting to client={client.remote_address}, "
                            f"response={response!r}",
                            flush=True,
                        )

                        await client.send(response)
                        
                        print(
                            f"DBG: broadcast send OK to client={client.remote_address}",
                            flush=True,
                        )
                        
                    except websockets.exceptions.ConnectionClosed as e:
                        print(
                            f"DBG: broadcast client closed: {client.remote_address} {e!r}",
                            flush=True,
                        )

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
