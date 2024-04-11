from datetime import datetime
from time import time

class Helper:
    def get_game(self, user): return self.games.get(user['user_id'])
    
    def add_notification(self, u, notification):
        if 'notifications' not in u: u['notifications'] = []
        u['notifications'].append(notification)

    def get_end_of_season(self):
        cur_date = datetime.now()

        year = cur_date.year
        month = cur_date.month + 1
        if month == 13: month = 1; year += 1

        return [year, month]

    def get_user(self, session_id: str | None = None, login: str | None = None, password: str | None = None, user_id: int | None = None):
        if user_id: return self.data['users'].get(user_id)
        elif login and password:
            user_id = self.data['logins'].get(login.lower())
            if not user_id: return

            user = self.data['users'].get(user_id)
            if user['password'] == password: return user

            with self.lock_manager.get_lock(session_id):
                if self.security.incorrect_login(session_id): raise Exception('Forbidden 403')
            
            raise Exception('Невірний пароль.')

        elif session_id:
            user_id = self.data['sessions'].get(session_id)

            if not user_id:
                return
            
            user = self.data['users'].get(user_id)

            return user

    def delete_account(self, user):
        for _ in range(len(user['sessions'])): self.remove_session(user, user['sessions'][0])

        del self.data['logins'][user['login'].lower()]
        del self.data['users'][user['user_id']]

        self.remove_ip(user['ip'], user)
        if user['global_pos'] != None: del self.data['global_top'][str(user['global_pos'])]

    def transform_digit(self, digit):
        digit = str(digit)
        for i in range((len(digit) - 1) // 3):
            index = -(i + 1) * 3 - i
            digit = digit[: index] + ' ' + digit[index: ]

        return digit

    def update_user_state(self, user, first_time = False):
        cur_time = int(time())
        if user['energy']['count'] < 10:
            delta = cur_time - user['energy']['time']
            
            if delta >= 3600:
                delta = delta // 3600
                user['energy']['count'] = user['energy']['count'] + delta

                if user['energy']['count'] >= 10: user['energy']['count'] = 10; user['energy']['time'] = None
                else: user['energy']['time'] += delta * 3600

        game = self.get_game(user)
        if game:
            if cur_time - game['start_time'] >= 3600:
                reward = self.end_game(user, game)
                if reward and first_time: self.add_notification(user, f'Гра завершена через неактивність.\nОтримано балів: {self.transform_digit(reward)}.')

    def check_ip(self, ip):
        data = self.data['ips'].get(ip)
        return data and len(data) >= 2 and False
    
    def reg_ip(self, ip, user):
        data = self.data['ips'].get(ip)
        if not data: data = []; self.data['ips'][ip] = data

        data.append(user['user_id'])
    
    def remove_ip(self, ip, user):
        data = self.data['ips'].get(ip)
        
        data.remove(user['user_id'])
        if not len(data): del self.data['ips'][ip]

    def add_to_top(self, user, type):
        key = ['season_pos', 'global_pos'][type]
        top = self.data[['season_top', 'global_top'][type]]

        top['members'] += 1
        user[key] = top['members']
        top[str(user[key])] = user['user_id']

    def end_game(self, user, game):
        reward = game['score']
        
        if user['season_pos'] == None:
            self.add_to_top(user, 0)
        
        user['level']['exp'][0] += reward
        while user['level']['exp'][0] >= user['level']['exp'][1]:
            user['level']['exp'][0] -= user['level']['exp'][1]

            user['level']['level'] += 1
            user['level']['exp'][1] += 100
            
        user['season_score'] += reward
        self.update_top(0, user)

        del self.games[user['user_id']]
        return reward
    
    def update_top(self, top_type, user):
        top_types = ['season_top', 'global_top']
        pos_types = ['season_pos', 'global_pos']
        score_types = ['season_score', 'global_score']
        
        with self.lock_manager.get_lock('top'):
            top = self.data[top_types[top_type]]
            pos = user[pos_types[top_type]]

            while pos != 1:
                u = self.data['users'][top[str(pos - 1)]]
                if u[score_types[top_type]] < user[score_types[top_type]]:
                    u[pos_types[top_type]] += 1
                    top[str(pos)] = u['user_id']
                    
                    pos -= 1

                else: break

            if pos != user[pos_types[top_type]]:
                top[str(pos)] = user['user_id']
                user[pos_types[top_type]] = pos
                
                return True
    
    def reset_sessions(self, user):
        length = len(user['sessions'])
            
        while 1 < length:
            length -= 1
            session = user['sessions'].pop(1)
            del self.data['sessions'][session['session_id']]
    
    def clear_sessions(self, user):
        i = 0
        cur_time = time()
        length = len(user['sessions'])
        while i < length:
            session = user['sessions'][i]
            if i != 0 and session['session_id'] == '':
                user['sessions'].pop(i)
                    
                i -= 1
                length -= 1
            
            elif cur_time - session['time'] >= 3600 * 24 * 7:
                user['sessions'].pop(i)
                
                if session['session_id'] != '':
                    del self.data['sessions'][session['session_id']]
                
                i -= 1
                length -= 1
            
            i += 1
    
    def remove_session(self, user, session = None, session_id = None):
        if not session:
            session = self.get_session(user, session_id)
            if not session: return

        user['sessions'].remove(session)
        del self.data['sessions'][session['session_id']]
