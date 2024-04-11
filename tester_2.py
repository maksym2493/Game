tasks_count = 10
log = True

import asyncio

from time import time
from json import loads
from math import log10
from aiofiles import open
from aiohttp import ClientSession

class Client:
    def __init__(self):
        self.api = 'http://127.0.0.1:5000/api/'
        self.session = ClientSession()
    
    async def get(self, path, **params):
        response = await self.session.get(self.api + path, params = params)
        
        try: return await response.json()
        except: return await response.text()
    
    async def close(self):
        await self.session.close()

error = 0
requests = 0
async def task(index):
    global error
    global requests
    
    client = Client()
    start_time = time()
    
    try:
        user_data = await client.get('login', login = f'User {index:0{int(log10(tasks_count)) + 1}}', password = '123456')
        
        device_id = user_data['result']['device_id']
        user_id = user_data['result']['user']['user_id']
        
        requests += 1
        if log: print(f'[ {index:{int(log10(tasks_count)) + 1}} ] [ {requests} ] Auth time: {round(time() - start_time, 6)} s.')
        
        for i in range(10):
            start_time = time()
            await client.get('start_game', device_id = device_id)
            
            requests += 1
            if log: print(f'[ {index:{int(log10(tasks_count)) + 1}} ] [ {requests} ] Create game: {round(time() - start_time, 6)} s.')
            
            async with open(f'games/{user_id}.json', 'r') as file:
                game_data = loads(await file.read())
                
                end = False
                while not end:
                    for i in range(25):
                        row = game_data[i]
                        
                        for j in range(25):
                            
                            cell = row[j]
                            
                            if cell['type'] and not cell['opened']:
                                start_time = time()
                                opened_cells = await client.get('open_cell', device_id = device_id, i = i, j = j)
                                
                                requests += 1
                                if log: print(f'[ {index:{int(log10(tasks_count)) + 1}} ] [ {requests} ] Open cell: {round(time() - start_time, 6)} s.')
                                
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
    global error
    global requests
    start_time = time()
    
    tasks = [asyncio.create_task(task(i + 1)) for i in range(tasks_count)]
    await asyncio.gather(*tasks)
    
    print(f'Total errors: {error}.')
    print(f'Total requests: {requests}.')
    print(f'Total time: {round(time() - start_time, 6)} s.')

asyncio.run(main())