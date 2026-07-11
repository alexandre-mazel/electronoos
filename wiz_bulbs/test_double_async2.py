import asyncio
import threading

async def loop1():
    while True:
        print("Loop 1 running")
        await asyncio.sleep(1)

async def loop2():
    while True:
        print("Loop 2 running")
        await asyncio.sleep(1.5)

def run_loop(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)

# Start each loop in its own thread
threading.Thread(target=run_loop, args=(loop1(),), daemon=True).start()
threading.Thread(target=run_loop, args=(loop2(),), daemon=True).start()

# Keep main thread alive
asyncio.get_event_loop().run_forever()