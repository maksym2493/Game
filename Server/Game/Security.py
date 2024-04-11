from time import time
from threading import Lock

class Security:
    def __init__(self):
        self.data = {}
        self.lock = Lock()
    
    def get_user(self, ip, cur_time):
        user = self.data.get(ip)
        if user: return user

        user = {}

        self.update_user(user, 'web', cur_time)
        self.update_user(user, 'api', cur_time)
        self.update_login(user, cur_time)
        
        with self.lock: self.data[ip] = user
        
        return user
    
    def check_web(self, ip, check = False):
        cur_time = time()
        user = self.get_user(ip, cur_time)

        res_1 = False
        if not check: res_1 = self.check_api(ip, True)
        res_2 = self.check_user(user, 'web', cur_time, 'second', 1, 20, 10, check)
        res_3 = self.check_user(user, 'web', cur_time, 'minute', 60, 60, 60, check)
        res_4 = self.check_user(user, 'web', cur_time, 'hour', 3600, 120, 3600, check)
        res_5 = self.check_user(user, 'web', cur_time, 'day', 86400, 720, 86400, check)

        return res_1 or res_2 or res_3 or res_4 or res_5

    def check_api(self, ip, check = False):
        cur_time = time()
        user = self.get_user(ip, cur_time)

        res_1 = False
        if not check: res_1 = self.check_web(ip, True)
        res_2 = self.check_user(user, 'api', cur_time, 'second', 1, 10, 10, check)
        res_3 = self.check_user(user, 'api', cur_time, 'minute', 60, 150, 60, check)
        res_4 = self.check_user(user, 'api', cur_time, 'hour', 3600, 2250, 3600, check)
        res_5 = self.check_user(user, 'api', cur_time, 'day', 86400, 13500, 86400, check)
        
        return res_1 or res_2 or res_3 or res_4 or res_5

    def check_user(self, user, type, cur_time, key, max_time, max_value, add_time, only_check = False):
        data = user[type][key]
        delta = cur_time - data['time']
        
        if delta >= max_time:
            delta = 0
            self.update_user(user, type, cur_time, key)
        
        if not only_check: data['count'] += 1
        
        if data['count'] >= max_value:
            if not only_check:
                max_time = 3600 * 24 - max_time
                
                if delta < max_time:
                    delta = max_time - delta
                    if delta < add_time: data['time'] += delta
                    else: data['time'] += add_time
            
            return True

    def incorrect_login(self, ip, check_only = False):
        cur_time = time()
        user = self.get_user(ip, cur_time)

        login = user['login']
        delta = cur_time - login['time']
        
        if delta >= 3600:
            self.update_login(user, cur_time)

            delta = 0
            login = user['login']
        
        if not check_only: login['count'] += 1
        
        if login['count'] >= 5:
            if not check_only:
                if delta < 82_800:
                    delta = 82_800 - delta
                    if delta < 3600: login['time'] += delta
                    else: login['time'] += 3600
    
            return True

    def update_user(self, user, type, cur_time, key = None):
        if not key:
            user[type] = {
                'second': {
                    'count': 0,
                    'time': cur_time
                },
                
                'minute': {
                    'count': 0,
                    'time': cur_time
                },
                
                'hour': {
                    'count': 0,
                    'time': cur_time
                },
                
                'day': {
                    'count': 0,
                    'time': cur_time
                },
            }
        
        else:
            user[type][key]['count'] = 0
            user[type][key]['time'] = cur_time

    def update_login(self, user, cur_time):
        user['login'] = {
            'count': 0,
            'time': cur_time
        }
    
    def clear(self, lock_manager):
        for_delete = []
        types = ['api', 'web']
        max_times = [1, 60, 3600, 86400]
        second_types = ['second', 'minute', 'hour', 'day']
        
        with self.lock: ips = list(self.data.keys())
        
        for ip in ips:
            with lock_manager.get_lock(ip):
                cur_time = time()
                user = self.data.get(ip)
                
                need_delete = True
                for type in types:
                    for second_type, max_time in zip(second_types, max_times):
                        data = user[type][second_type]
                        delta = cur_time - data['time']
                        
                        if delta < max_time:
                            need_delete = False
                            
                            break
                        
                    if need_delete: break
                
                if need_delete: del self.data[ip]