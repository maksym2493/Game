r = None
R = [50, 75, 100, 125]
accounts = [10, 100, 1_000, 10_000, 100_000, 1_000_000]

game = None
tasks_count = 10
max_requests = 1_000

import asyncio

from numpy import var
from time import time
from json import loads
from math import log10
from aiofiles import open
from aiohttp import ClientSession

def get_game():
    from shutil import rmtree
    from time import sleep
    
    try: rmtree('Data')
    except: pass

    from Server import game
    globals()['game'] = game

    sleep(5)

get_game()

class Client:
    def __init__(self):
        self.api = 'http://127.0.0.1:5000/api/'
        self.session = ClientSession()
    
    async def get(self, path, **params):
        global error
        global results
        global requests
        global load_testing
        
        if results:
            while True:
                pos = 0
                cur_time = time()
                length = len(results)
                
                while pos < length:
                    if cur_time - results[pos] < 1: pos += 1
                    else: results.pop(pos); length -= 1

                if length != r: break
                await asyncio.sleep(0.0001)
        
        if error: return
        if requests == max_requests: return
        
        requests += 1
        results.insert(0, time())
        
        start_time = time()
        
        response = await self.session.get(self.api + path, params = params)
        
        try: result = await response.json()
        except: result = await response.text()
        
        load_testing.append(time() - start_time)
        
        return result
    
    async def close(self):
        await self.session.close()

error = 0
requests = 0
results = []
load_testing = []

async def task(index):
    global error
    global requests
    
    client = Client()
    
    try:
        user_data = await client.get('login', login = f'User {index:03}', password = '123456')
        if not user_data: return
        
        device_id = user_data['result']['device_id']
        user_id = user_data['result']['user']['user_id']
        
        for _ in range(10):
            res = await client.get('start_game', device_id = device_id)
            if not res: return
            
            async with open(f'games/{user_id}.json', 'r') as file:
                game_data = loads(await file.read())
                
                end = False
                while not end:
                    for i in range(25):
                        row = game_data[i]
                        
                        for j in range(25):
                            
                            cell = row[j]
                            
                            if cell['type'] and not cell['opened']:
                                opened_cells = await client.get('open_cell', device_id = device_id, i = i, j = j)
                                if not opened_cells: return
                                
                                if type(opened_cells['result']) == list:
                                    for cell in opened_cells['result']:
                                        game_data[cell['pos'][0]][cell['pos'][1]]['opened'] = True

                                else: end = True
                                
                                break
                        
                        else: continue
                        
                        break
    
    except Exception as e:
        print(e)
        error += 1
    
    finally:
        await client.close()

async def wait_process(process):
    await process.wait()

async def main():
    global r
    global error
    global requests
    global load_testing
    
    number = 0
    created = 0
    
    tasks = []
   
    for ac in accounts:
        if created != ac:
            error = 0
            requests = 0
            results.clear()
            load_testing.clear()
            
            r = 125
            p = False
            client = Client()
            
            print()
            while True:
                created += 1
                game.main('127.0.0.1', 'login', login = f'User {created:03}', password = '123456')
                print(f'\033[A[ Generation, {transform_digit(ac)} ] [ {transform_digit(created): >{int(log10(ac)) + 1 + int((len(str(ac)) - 1) / 3)}} ]')

                if created == ac: break
            
            print()
            await client.close()
        
        await asyncio.sleep(10)
        
        process = await asyncio.create_subprocess_exec(
            'python', '__main__.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        server_task = asyncio.create_task(process.communicate())
        
        await asyncio.sleep(5)
        
        error = 0
        requests = 0
        results.clear()
        load_testing.clear()
        
        for r in R:
            print()
            while True:
                await asyncio.sleep(0.0001)
                
                pos = 0
                length = len(tasks)
                while pos < length:
                    if tasks[pos].done(): tasks.pop(pos); length -= 1
                    else: pos += 1
                
                while length != tasks_count: number += 1; tasks.append(asyncio.create_task(task(number))); length += 1
                
                if load_testing:
                    counts = int((len(str(R[-1])) - 1) / 3)
                    rps = transform_digit(len(results))
                    
                    if error or requests == max_requests: print(f'\033[A[ Results, {transform_digit(ac)} ] [ {r: >{int(log10(R[-1])) + 1}} ] RPS: {rps: >{int(log10(R[-1])) + 1 + counts}}. Min: {min(load_testing):13.10f}. Max: {max(load_testing):13.10f}. AVG: {sum(load_testing) / len(load_testing):13.10f}. VAR: {var(load_testing):13.10f}. [ {transform_digit(requests)} ]')
                    else: print(f'\033[A[ Testing, {transform_digit(ac)} ] [ {r: >{int(log10(R[-1])) + 1}} ] RPS: {rps: >{int(log10(R[-1])) + 1 + counts}}. Min: {min(load_testing):13.10f}. Max: {max(load_testing):13.10f}. AVG: {sum(load_testing) / len(load_testing):13.10f}. VAR: {var(load_testing):13.10f}. [ {transform_digit(requests): >{int(log10(max_requests)) + 1 + int((len(str(max_requests)) - 1) / 3)}} ]')
                
                if error: break
                if requests == max_requests: break
            
            await asyncio.sleep(1)
            
            error = 0
            requests = 0
            results.clear()
            load_testing.clear()
        
        print()
        print()
        
        server_task.cancel()
        process.terminate()

def transform_digit(digit):
    digit = str(digit)
    
    for i in range(int((len(digit) - 1) / 3)):
        index = -(i + 1) * 3 - i
        digit = digit[0: index] + ' ' + digit[index: ]
    
    return digit

asyncio.run(main())