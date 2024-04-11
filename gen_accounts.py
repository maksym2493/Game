import asyncio
from math import log10
from aiohttp import ClientSession

async def wait_for_end(tasks, max_count = None):
    while (max_count != None and len(tasks) == max_count) or len(tasks):
        pos = 0
        while pos < len(tasks):
            if tasks[pos].done():
                tasks.pop(pos)
                continue
            
            pos += 1
        
        await asyncio.sleep(0.01)

async def main():
    count = 0
    max_count = 20_000
    max_tasks_count = 100
    
    tasks = []
    session = ClientSession()
    
    while True:
        await wait_for_end(tasks, max_tasks_count)
        
        print(f'[ {(count + 1):0{int(log10(max_count)) + 1}} ] Genereting...')
        tasks.append(asyncio.create_task(session.get(f'http://127.0.0.1:5000/api/login?login={(count + 1):0{int(log10(max_count)) + 1}}&password=123456')))
        
        count += 1
        if count == max_count:
            await wait_for_end(tasks)
            break
    
    await session.close()

asyncio.run(main())