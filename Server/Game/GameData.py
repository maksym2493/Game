from .Helper import Helper
from .Security import Security
from .LockManager import LockManager

from os import mkdir
from json import load, dump
from time import time, sleep
from threading import Thread, Lock

class GameData(Helper):
    def __init__(self):
        self.load()
        self.games = {}
        self.last_update = 0
        self.last_update_2 = 0
        self.need_update = False
        self.security = Security()

        self.mutex = Lock()
        self.can_work = True
        self.queue_length = 0
        self.lock_manager = LockManager()
        Thread(target = self.updator).start()

    def load(self):
        try: self.data = load(open('Data/data.json', 'r', encoding = 'utf-8'))
        except:
            try: mkdir('Data')
            except: pass
            
            self.data = {
                'users': {},
                'logins': {},
                'sessions': {},

                'next_user_id': 1,
                'end_of_season': self.get_end_of_season(),

                'ips': {},
                'global_top': {'members': 0},
                'season_top': {'members': 0},
            }

    def dump(self):
        dump(self.data, open('Data/data.json', 'w', encoding = 'utf-8'), ensure_ascii = False)

    def add_shift(self, shifts, shift):
        for i, s in enumerate(shifts):
            if s > shift: shifts.insert(i, shift); return

        shifts.append(shift)

    def get_shift(self, shifts, pos):
        shift = 0
        for s in shifts:
            if s < pos: shift -= 1
            else: break

        return shift

    def repaire_shifts(self, shifts, old_pos, new_pos):
        for i, s in enumerate(shifts):
            if old_pos <= s: break
            if old_pos > s and new_pos <= s: shifts[i] += 1

    def updator(self):
        try:
            while True:
                end_of_season = self.get_end_of_season()

                if end_of_season != self.data['end_of_season']:
                    with self.mutex:
                        self.can_work = False
                    
                    while True:
                        with self.mutex:
                            if not self.queue_length: break
                        
                        sleep(0.0001)
                    
                    self.data['season_top'] = {'members': 0}
                    self.data['end_of_season'] = end_of_season

                    shifts = []
                    user_ids = []

                    for u in self.data['users'].values():
                        if not u['season_pos']:
                            user_ids.append(u['user_id'])
                            if u['global_pos']:
                                self.add_shift(shifts, u['global_pos'])

                            continue

                        pos = u['season_pos']

                        u['season_score'] = 0
                        u['season_pos'] = None

                        notification = f'Сезон завершено!\nВи зайняли {pos}-е місце!'
                            
                        if pos <= 1000:
                            score = 1000 - (pos - 1)
                            if u['global_pos'] == None: self.add_to_top(u, 1)
                                
                            u['global_score'] += score
                            notification += f' Нараховані за перемогу бали: {self.transform_digit(score)}!'

                            old_pos = u['global_pos']
                            if self.update_top(1, u):
                                self.repaire_shifts(shifts, old_pos, u['global_pos'])

                        self.add_notification(u, notification)

                    for user_id in user_ids: self.delete_account(self.data['users'][user_id])

                    self.data['global_top'] = {'members': 0}
                    for u in self.data['users'].values():
                        shift = self.get_shift(shifts, u['global_pos'])

                        u['global_pos'] += shift
                        self.data['global_top']['members'] += 1
                        self.data['global_top'][str(u['global_pos'])] = u['user_id']

                    self.need_update = True
                    with self.mutex: self.can_work = True

                cur_time = int(time())
                if cur_time - self.last_update >= 3600:
                    self.last_update = cur_time
                    for u in self.data['users'].values():
                        with self.lock_manager.get_lock(u['user_id']):
                            self.clear_sessions(u)
                            self.update_user_state(u)
                
                if cur_time - self.last_update_2 >= 3600:
                    self.last_update_2 = cur_time
                    self.security.clear(self.lock_manager)
                
                can = False
                with self.mutex:
                    if self.need_update:
                        can = True
                        self.need_update = False
                
                if can:
                    with self.lock_manager.get_lock('register'): self.dump()

                #print('All is good.')
                sleep(10)
        
        except Exception as e: open('f.txt', 'w', encoding = 'utf-8').write(str(e))
        
        finally:
            with self.lock_manager.get_lock('register'): self.dump()