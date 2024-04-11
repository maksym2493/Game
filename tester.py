from requests import Session

from os import system
from time import sleep
from threading import Thread

class Tester:
    def __init__(self):
        self.session = Session()
        self.api = 'http://127.0.0.1:5000/api/'
    
    def test(self, path, **params):
        response = self.session.get(self.api + path, params = params)
        
        try: return response.json()
        except: return response.text

tester = Tester()

try: open('Data/data.json', 'w')
except: pass

import subprocess

def run_script():
    subprocess.run(['python', '__main__.py'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

Thread(target=run_script).start()
sleep(5)

#1A -> 1A-C -> 1B -> 1B-A -> 1B-A-B -> 1B-C -> 1B-C-A -> 1B-C-A-F -> 1B-C-B-B -> 1B-C-C -> 1B-F -> 1D
data = tester.test(
    'login',
    login = 'Maksym',
    password = 'maksym0000'
)
device_id = data['result']['device_id']

#1A -> 1B -> 1B-A -> 1B-A-E -> 1D
data2 = tester.test(
    'login',
    login = 'Maksym',
    password = 'maksym0000'
)
device_id2 = data2['result']['device_id']

print(data)
print()

print(data2)
print()

tests = [
    #1A -> 1A-C -> 1B -> 1B-A -> 1B-A-C -> 1B-A-C-B -> 1B-A-C-C -> 1B-A-D -> 1B-B -> 1C
    [
        'login',
        {
            'login': 'maksym',
            'password': 'asdsa'
        }
    ],
    
    #2A -> 2A-G -> 2B
    [
        'get_profile',
        {
            'device_id': '1'
        }
    ],
    
    #2A -> 2A-H -> 3A
    [
        'get_profile',
        {
            'device_id': device_id
        }
    ],
    
    #1B -> 1B-C -> 1B-C-A -> 1B-C-A-A -> 1B-C-E -> 1B-D -> 1C
    [
        'login',
        {
            'login': '1',
            'password': '1',
        }
    ],
    
    #1B -> 1B-C -> 1B-C-A -> 1B-C-A-A -> 1B-C-F -> 1B-D -> 1C
    [
        'login',
        {
            'login': 'maksym2',
            'password': 'sad',
        }
    ],
    
    [
        'login',
        {
            'login': 'maksym2',
            'password': 'maksym0000',
        }
    ],
    
    #1B -> 1B-C -> 1B-C-D -> 1C
    [
        'login',
        {
            'login': 'maksym3',
            'password': 'maksym0000',
        }
    ],
    
    #3B
    [
        'get_profile',
        {
            'device_id': device_id,
            'user_id': 'q',
        }
    ],
    
    #3C
    [
        'get_profile',
        {
            'device_id': device_id,
            'user_id': data['result']['user']['user_id'],
        }
    ],
    
    #3D -> 3D-A -> 3E
    [
        'get_profile',
        {
            'device_id': device_id,
            'user_id': 3,
        }
    ],
    
    #3D -> 3A
    [
        'get_profile',
        {
            'device_id': device_id,
            'user_id': 2,
        }
    ],
    
    #4A
    [
        'change_login',
        {
            'device_id': device_id,
            'login': data['result']['user']['login'],
        }
    ],
    
    #4B
    [
        'change_login',
        {
            'device_id': device_id,
            'login': 'Maksym2',
        }
    ],
    
    #4C -> 4C-B -> 4D
    [
        'change_login',
        {
            'device_id': device_id,
            'login': '   Maksym2',
        }
    ],
    
    #4C -> 4C-C -> 4D
    [
        'change_login',
        {
            'device_id': device_id,
            'login': ' Maksym2',
        }
    ],
    
    #4C -> 4C-D -> 4D
    [
        'change_login',
        {
            'device_id': device_id,
            'login': 'Mak  sym2',
        }
    ],
    
    #4C -> 4C-E -> 4D
    [
        'change_login',
        {
            'device_id': device_id,
            'login': 'Mak!sym2',
        }
    ],
    
    #4E -> 4F
    [
        'change_login',
        {
            'device_id': device_id,
            'login': 'Maksym1',
        }
    ],
    
    #4F
    [
        'change_login',
        {
            'device_id': device_id,
            'login': 'MaksyM1',
        }
    ],
    
    #5B
    [
        'change_password',
        {
            'device_id': device_id,
            'old_password': 'MaksyM1',
            'new_password': 'MaksyM1',
            'repeated_password': 'MaksyM1',
        }
    ],
    
    #5C
    [
        'change_password',
        {
            'device_id': device_id,
            'old_password': 'maksym0000',
            'new_password': 'maksym0000',
            'repeated_password': 'MaksyM1',
        }
    ],
    
    #5D
    [
        'change_password',
        {
            'device_id': device_id,
            'old_password': 'maksym0000',
            'new_password': 'maksym1111',
            'repeated_password': 'maksym0000',
        }
    ],
    
    #5E
    [
        'change_password',
        {
            'device_id': device_id,
            'old_password': 'maksym0000',
            'new_password': '123',
            'repeated_password': '123',
        }
    ],
    
    #5F
    [
        'change_password',
        {
            'device_id': device_id,
            'old_password': 'maksym0000',
            'new_password': 'maksym1111',
            'repeated_password': 'maksym1111',
        }
    ],
    
    #6A -> 6A-A -> 6B
    [
        'get_season_top',
        {
            'device_id': device_id,
            'page': 'q'
        }
    ],
    
    #6A -> 6A-E -> 6C
    [
        'get_season_top',
        {
            'device_id': device_id,
        }
    ],
    
    #7A -> 7A-B -> 7B
    [
        'get_global_top',
        {
            'device_id': device_id,
            'page': 0
        }
    ],
    
    #7A -> 7A-D -> 7C
    [
        'get_global_top',
        {
            'device_id': device_id,
        }
    ],
    
    #7A -> 7A-C -> 7B
    [
        'get_global_top',
        {
            'device_id': device_id,
            'page': 2
        }
    ],
    
    #7A -> 7С
    [
        'get_global_top',
        {
            'device_id': device_id,
            'page': 1
        }
    ],
    
    #10A
    [
        'open_cell',
        {
            'device_id': device_id,
            'i': 0,
            'j': 0,
        }
    ],
    
    #11A
    [
        'mark_cell',
        {
            'device_id': device_id,
            'i': 0,
            'j': 0,
        }
    ],
]

for test in tests:
    print(test, tester.test(test[0], **test[1]))
    print()

#9C
game_data = tester.test('start_game', device_id = device_id)
print(game_data)
print()

game_data = game_data['result']

#9A
print(tester.test('start_game', device_id = device_id))
print()

i = 0
j = 0
for i in range(25):
    for j in range(25):
        found = False
        cur_cell = [i, j]
        
        for cell in game_data['opened']:
            if cell['pos'] == cur_cell:
                found = True
                break
        
        if not found:
            break

#10B
print(tester.test('open_cell', device_id = device_id, i = 'a', j = 'b'))
print()

#10C
print(tester.test('open_cell', device_id = device_id, i = game_data['opened'][0]['pos'][0], j = game_data['opened'][0]['pos'][1]))
print()

#11B
print(tester.test('mark_cell', device_id = device_id, i = 0, j = 26))
print()

#11C
print(tester.test('mark_cell', device_id = device_id, i = game_data['opened'][0]['pos'][0], j = game_data['opened'][0]['pos'][1]))
print()

#11D
print(tester.test('mark_cell', device_id = device_id, i = i, j = j))
print()

from json import load

game_data = load(open('Game.txt'))
for i in range(25):
    row = game_data[i]
    
    for j in range(25):
        cell = row[j]
        
        if not cell['type']:
            #10D
            print(tester.test('open_cell', device_id = device_id, i = i, j = j))
            print()
            
            break
    
    else: continue
    
    break

tester.test('start_game', device_id = device_id)
print()

end = False
game_data = load(open('Game.txt'))

bombs_count = 0
for row in game_data:
    for cell in row:
        if not cell['type']: bombs_count += 1

from pandas import DataFrame
from tabulate import tabulate

def print_game(game_data, opened_pos):
    table = []
    for i, row in enumerate(game_data):
        table.append([])
        for j, cell in enumerate(row):
            if opened_pos == [i, j]:
                table[i].append('\033[31m' + 'O' + '\33[37m')
            
            elif cell['type'] and cell['opened']:
                table[i].append('\033[32m' + str(cell['count']) + '\33[37m')
            
            else:
                table[i].append('X')
    
    print(tabulate(DataFrame(table), showindex = False))

reward = (25 * 25 - bombs_count) * 1.5

while not end:
    for i in range(25):
        row = game_data[i]
        
        for j in range(25):
            
            cell = row[j]
            
            if cell['type'] and not cell['opened']:
                #10E
                opened_cells = tester.test('open_cell', device_id = device_id, i = i, j = j)
                if type(opened_cells['result']) == list:
                    for cell in opened_cells['result']:
                        game_data[cell['pos'][0]][cell['pos'][1]]['opened'] = True
                    
                    #print_game(game_data, [i, j])
                    #input()
                
                else:
                    #10F
                    print(reward)
                    print(opened_cells)
                    print()
                    end = True
                
                break
        
        else: continue
        
        break

while True:
    status = tester.test('start_game', device_id = device_id)
    if status['status'] == 'Error':
        #9B
        print(status)
        print()
        
        break
    
    game_data = load(open('Game.txt'))
    
    for i in range(25):
        row = game_data[i]
        
        for j in range(25):
            cell = row[j]
            
            if not cell['type']:
                tester.test('open_cell', device_id = device_id, i = i, j = j)
                
                break
        
        else: continue
        
        break

#1B -> 1B-a -> 1B-G -> 1D
print(device_id)
data = tester.test('login', device_id = '1', login = 'maksym1', password = 'maksym1111')
print(data)
print()

#1B -> 1B-a -> 1B-E -> 1B-F -> 1D
print(tester.test('login', device_id = device_id, login = 'maksym1', password = 'maksym1111'))
print()

#2C
print(tester.test('logout', device_id = device_id))
print()

#8A
print(tester.test('get_profile', device_id = data['result']['device_id']))
print()

#2D
print(tester.test('reset_sessions', device_id = data['result']['device_id']))
print()

data = tester.test(
    'login',
    login = 'Maksym1',
    password = 'maksym1111'
)

for i in range(3):
    res = tester.test(
        'login',
        login = 'Maksym1',
        password = 'maksym0000'
    )
    
    #1B -> 1B-A -> 1B-A-C-B -> 1B-A-C-E -> 1B-A-C-G -> 1B-A-F -> 1B-B -> 1C
    print(res)
    print()

#1C
print(tester.test(
    'login',
    login = 'Maksym1',
    password = 'maksym0000'
))
print()

#5A
print(tester.test(
    'change_password',
    device_id = data['result']['device_id'],
    old_password = 'maksym0000',
    new_password = 'maksym0000',
    repeated_password = 'maksym0000',
))