import asyncio

async def task1():
    while True:
        print("Task 1 running...")
        await asyncio.sleep(1)

async def task2():
    while True:
        print("Task 2 running...")
        await asyncio.sleep(2)

async def main():
    # Run both tasks concurrently in the same loop
    await asyncio.gather(task1(), task2())
    
    
asyncio.run(main())