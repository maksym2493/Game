r = None
R = [10, 25, 50, 75, 100, 125]

tasks_count = 10
max_requests = 1_000

import asyncio

from time import time
from json import loads
from math import log10
from aiofiles import open
from aiohttp import ClientSession

def run_server():
    import subprocess
    
    from os import remove
    from time import sleep
    from threading import Thread
    
    try: remove('Data/data.json')
    except: pass

    def run_script():
        subprocess.run(['python', '__main__.py'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    Thread(target=run_script).start()
    sleep(5)

run_server()

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
    
    except Exception as e: print(f'[ {index} ] Error: {e}.'); error += 1
    
    finally:
        await client.close()

async def main():
    global r
    global error
    global requests
    global load_testing
    
    tasks = [asyncio.create_task(task(i + 1)) for i in range(tasks_count)]
    
    i = tasks_count + 1
    
    for r in R:
        print()
        while True:
            await asyncio.sleep(0.0001)
            
            pos = 0
            length = len(tasks)
            while pos < length:
                if tasks[pos].done(): tasks.pop(pos); length -= 1
                else: pos += 1
            
            while length != tasks_count: tasks.append(asyncio.create_task(task(i))); i += 1; length += 1
            
            if load_testing:
                counts = int((len(str(R[-1])) - 1) / 3)
                rps = transform_digit(len(results))
                
                if error or requests == max_requests: print(f'\033[A[ Results ] [ {r: >{int(log10(R[-1])) + 1}} ] RPS: {rps: >{int(log10(R[-1])) + 1 + counts}}. Min: {min(load_testing):13.10f}. Max: {max(load_testing):13.10f}. AVG: {sum(load_testing) / len(load_testing):13.10f}. [ {transform_digit(requests)} ]')
                else: print(f'\033[A[ Testing ] [ {r: >{int(log10(R[-1])) + 1}} ] RPS: {rps: >{int(log10(R[-1])) + 1 + counts}}. Min: {min(load_testing):13.10f}. Max: {max(load_testing):13.10f}. AVG: {sum(load_testing) / len(load_testing):13.10f}. [ {transform_digit(requests): >{int(log10(max_requests)) + 1 + int((len(str(max_requests)) - 1) / 3)}} ]')
            
            if error: break
            if requests == max_requests: break
        
        requests = 0
        results.clear()
        load_testing.clear()

def transform_digit(digit):
    digit = str(digit)
    
    for i in range(int((len(digit) - 1) / 3)):
        index = -(i + 1) * 3 - i
        digit = digit[0: index] + ' ' + digit[index: ]
    
    return digit

asyncio.run(main())