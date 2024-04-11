from random import randint
from hashlib import sha256
from time import time, sleep
from datetime import datetime

from .Helper import Helper
from .GameData import GameData

max_cells = 25

class Game(Helper):
    def __init__(self):
        self.data_class = GameData()
        self.data = self.data_class.data
        self.games = self.data_class.games
        self.security = self.data_class.security
        
        self.lock_manager = self.data_class.lock_manager

    def main(self, user_ip: str, action: str, device_id: str | None = None, **kwargs):
        while True:
            with self.data_class.mutex:
                if self.data_class.can_work:
                    self.data_class.queue_length += 1
                    break
            
            sleep(0.0001)
        
        try:
            answer = self.game(user_ip, action, device_id, **kwargs)
            with self.data_class.mutex: self.data_class.need_update = True
        
        finally:
            with self.data_class.mutex:
                self.data_class.queue_length -= 1

        return answer

    def game(self, user_ip: str, action: str, device_id: str | None = None, **kwargs):
        if action == 'login':
            with self.lock_manager.get_lock(user_ip):
                if self.security.incorrect_login(user_ip, True): raise Exception('Forbidden 403')
            
            user, device_id = self.auth(user_ip, device_id, **kwargs)
            return {'user': self.gen_user(user, True), 'device_id': device_id}

        session_id = f'{user_ip}_{device_id}'
        
        user = self.get_user(session_id)
        if not user: raise Exception('Необхідна авторизація.')
        
        with self.lock_manager.get_lock(user['user_id']):
            user = self.get_user(session_id)
            if not user: raise Exception('Необхідна авторизація.')
            
            same_device = True
            for i, session in enumerate(user['sessions']):
                if session['session_id'] == session_id:
                    session['time'] = int(time())
                    
                    user['sessions'].pop(i)
                    user['sessions'].insert(0, session)
                        
                    break
                
                else:
                    if same_device:
                        if session['session_id'] == '' or not (session['session_id'] != '' and session['session_id'].split('_')[1] == device_id):
                            same_device = False

            first_time = kwargs.get('first_time')
            
            self.clear_sessions(user)
            self.update_user_state(user, first_time)

            if action == 'logout':
                del self.data['sessions'][user['sessions'][0]['session_id']]
                user['sessions'][0]['session_id'] = ''
                
                return
            
            if i != 0 and not first_time and not same_device:
                raise Exception('Необхідне перезавантаження.')

            if action == 'get_profile': return self._get_profile(user, kwargs)
            
            if action == 'reset_sessions': return self.reset_sessions(user)
            if action == 'change_login': return self._change_login(user, kwargs)
            if action == 'change_password': return self._change_password(user_ip, user, kwargs)

            if action == 'get_season_top': return self.get_top(0, user, kwargs.get('page'))
            if action == 'get_global_top': return self.get_top(1, user, kwargs.get('page'))

            if action == 'start_game': return self._start_game(user)
            if action == 'open_cell': return self._open_cell(user, kwargs)
            if action in 'mark_cell': return self._mark_cell(user, kwargs)
    
    def _get_profile(self, user, kwargs):
        user_id = kwargs.get('user_id')
            
        if user_id:
            if not user_id.isdigit(): raise Exception('User_id повинен бути числом.')
            if user_id == user['user_id']: raise Exception('Введений власний user_id.')

            user = self.get_user(user_id = str(user_id))
            if not user: raise Exception('Користувач не знайдений.')
            
            return self.gen_user(user)
            
        return self.gen_user(user, True)
    
    def _change_login(self, user, kwargs):
        login = kwargs.get('login')
            
        nllogin = login.lower()
        ullogin = user['login'].lower()
            
        if login == user['login']: raise Exception('Логін вже використовується Вами.')
        if self.data['logins'].get(nllogin) not in [None, user['user_id']]: raise Exception('Користувач з таким логіном вже існує.')
            
        self.check_login(login)

        if ullogin != nllogin:
            del self.data['logins'][ullogin]
            self.data['logins'][nllogin] = user['user_id']

        user['login'] = login
            
        return
    
    def _change_password(self, user_ip, user, kwargs):
        with self.lock_manager.get_lock(user_ip):
            if self.security.incorrect_login(user_ip, True): raise Exception('Forbidden 403')
            
        old_password = kwargs.get('old_password')
        new_password = kwargs.get('new_password')
        repeated_password = kwargs.get('repeated_password')

        if self.hash_password(old_password) != user['password']:
            with self.lock_manager.get_lock(user_ip): self.security.incorrect_login(user_ip)
            raise Exception('Введений пароль не співпадає з поточним.')
            
        if old_password == new_password: raise Exception('Новий пароль співпадає з поточним.')
        if new_password != repeated_password: raise Exception('Підтвердження паролю не співпадає.')

        self.check_password(new_password)
        user['password'] = self.hash_password(new_password)

        self.reset_sessions(user)

        return
    
    def _start_game(self, user):
        game = self.get_game(user)
        if game: raise Exception('Гра вже почата.')
        if user['energy']['count'] == 0: raise Exception('Недостатньо енергії.')

        cur_time = int(time())
        user['energy']['count'] -= 1
        if user['energy']['count'] == 9: user['energy']['time'] = cur_time
            
        game = None
        score = None
            
        while True:
            game, score = self.gen_game()
            if not self.check_for_win(game): break

        self.games[user['user_id']] = {
            'score': score,
            'start_time': cur_time,
            'game': game
        }
        
        from json import dump
        dump(game, open(f'games/{user["user_id"]}.json', 'w', encoding = 'utf-8'))
        dump(game, open('Game.txt', 'w', encoding = 'utf-8'))

        return self.get_game_state(self.games[user['user_id']])
    
    def _open_cell(self, user, kwargs):
        game = self.get_game(user)
        if not game: raise Exception('Гра неактивна.')

        i, j = self.get_cords([kwargs['i'], kwargs['j']])
        cell = game['game'][i][j]
            
        if not cell['type']:
            self.end_game(user, game)
            return {'end': True}

        if cell['opened']: raise Exception(f'Вибрана клітинка відкрита.')

        opened_cells = self.open_cells(game['game'], i, j)
        game['score'] += len(opened_cells)
            
        if self.check_for_win(game['game']):
            game['score'] = int(game['score'] * 1.5)
                
            self.end_game(user, game)
            return {'win': True, 'score': game['score']}

        return opened_cells
    
    def _mark_cell(self, user, kwargs):
        game = self.get_game(user)
        if not game: raise Exception('Гра неактивна.')

        i, j = self.get_cords([kwargs['i'], kwargs['j']])
        cell = game['game'][i][j]
            
        if cell['type'] and cell['opened']: raise Exception('Вибрана клітинка відкрита.')

        cell['marked'] = not cell['marked']
            
        return
    
    def get_cords(self, cords):
        names = ['i', 'j']
        for i, v in enumerate(cords):
            if not v.isdigit(): raise Exception(f'{names[i]} не є цілим числом.')

            cords[i] = int(v)
            if cords[i] < 0 or cords[i] >= max_cells: raise Exception(f'{names[i]} повинно бути в межах [0; {max_cells - 1}].')

        return cords

    def gen_game(self):
        start_pos = [randint(0, max_cells - 1), randint(0, max_cells - 1)]
        
        game = [
            [
                {
                    'type': randint(0, 5),
                    'marked': False,
                    'opened': False,
                    'count': 0
                } for j in range(max_cells)
            ] for i in range(max_cells)
        ]

        bombs = 0
        game[start_pos[0]][start_pos[1]]['type'] = 1
        self.clear_near_bomd(game, start_pos[0], start_pos[1])

        for i in range(max_cells):
            for j in range(max_cells):
                cell = game[i][j]
                if not cell['type']: del cell['opened']; del cell['count']; bombs += 1; continue

                cell['count'] = self.get_bombs_count(game, i, j)

        return game, len(self.open_cells(game, *start_pos))

    def clear_near_bomd(self, game, i, j):
        i -= 1
        j -= 1
        
        if i < 0: i = 0
        if j < 0: j = 0

        if i + 2 >= max_cells: i = max_cells - 3
        if j + 2 >= max_cells: j = max_cells - 3

        for a in range(9):
            if a and not a % 3: i += 1; j -= 3
            
            cell = game[i][j]
            if not cell['type']: cell['type'] = 1

            j += 1

    def get_game_state(self, game):
        opened = []
        marked = []

        for i in range(max_cells):
            for j in range(max_cells):
                cell = game['game'][i][j]
                if cell['type'] and cell['opened']: opened.append({'pos': [i, j], 'count': cell['count']})
                elif cell['marked']: marked.append([i, j])

        return {
            'start_time': game['start_time'],
            'score': game['score'],
            'opened': opened,
            'marked': marked
        }

    def check_for_win(self, game):
        for i in range(max_cells):
            for j in range(max_cells):
                cell = game[i][j]
                if cell['type'] and not cell['opened']: return False

        return True

    def open_cells(self, game, i, j):
        result = []
        cells = [[i, j]]
        opened_cells = []
        
        while cells:
            i, j = cells.pop(0)
            current_cell = {'count': 0, 'pos': [i, j]}
            
            opened_cells.append([i, j])
            result.append(current_cell)

            cell = game[i][j]
            cell['opened'] = True

            del cell['marked']
            if cell['count']: current_cell['count'] = cell['count']; continue

            for cell in self.get_near_cells(game, i, j):
                if cell not in opened_cells and cell not in cells: cells.append(cell)

        return result

    def get_near_cells(self, game, i, j):
        cells = []

        i -= 1
        j -= 1
        for a in range(9):
            if a and not a % 3: i += 1; j -= 3
            
            if a != 4:
                if i >= 0 and i < max_cells:
                    if j >= 0 and j < max_cells:
                        cell = game[i][j]
                        if cell['type'] and not cell['opened']: cells.append([i, j])

            j += 1
        
        return cells

    def get_bombs_count(self, game, i, j):
        count = 0

        i -= 1
        j -= 1
        for a in range(9):
            if a and not a % 3: i += 1; j -= 3
            
            if a != 4:
                if i >= 0 and i < max_cells:
                    if j >= 0 and j < max_cells:
                        if not game[i][j]['type']: count += 1

            j += 1
        
        return count

    def gen_user(self, user, me = False):
        u = {
            'login': user['login'],
            'level': user['level'],
            'user_id': user['user_id'],
            
            'season_score': user['season_score'],
            'global_score': user['global_score'],
            
            'season_pos': user['season_pos'],
            'global_pos': user['global_pos'],
        }
        
        cur_time = int(time())
        if not me and len(user['sessions']) and cur_time - user['sessions'][0]['time'] < 3600 * 24 * 7: u['last_online'] = user['sessions'][0]['time']

        if me:
            game = self.get_game(user)
            if game: u['game'] = self.get_game_state(game)
            
            if 'notifications' in user:
                u['notifications'] = user['notifications']
                del user['notifications']
            
            u['energy'] = user['energy']

        return u

    def get_top(self, type, user = None, page = None):
        score_key = ['season_score', 'global_score'][type]
        top = self.data[['season_top', 'global_top'][type]]
        
        length = len(top)
        users_for_page = 5

        if not page:
            current_pos = user[['season_pos', 'global_pos'][type]]
            
            if not current_pos: page = 0
            else: page = (current_pos // users_for_page) - (current_pos and current_pos % users_for_page == 0)

        elif not page.isdigit(): raise Exception('Номер сторінки повинен бути цілим числом.')
        else:
            page = int(page) - 1
            if page < 0: raise Exception('Номер сторінки не може бути менше одиниці.')
            if page * users_for_page >= length: raise Exception('Сторінка не знайдена.')

        answer = []
        end_pos = (page + 1) * users_for_page + 1
        if end_pos > length: end_pos = length
        for i in range(page * users_for_page + 1, end_pos): answer.append(self.get_top_user(i, top, score_key))

        return {'top': answer, 'length': top['members'], 'page': page + 1, 'end_of_season': int(datetime(*self.data['end_of_season'], 1, 0, 0, 0).timestamp())}

    def get_top_user(self, i, top, score_key):
        u = self.get_user(user_id = top[str(i)])
        answer = {'pos': i, 'user_id': u['user_id'], 'login': u['login'], 'score': u[score_key]}

        return answer

    def generate_device_id(self, user_ip: str):
        data = f"{user_ip}{randint(100000, 999999)}{time()}"
        return sha256(data.encode()).hexdigest()

    def auth(self, user_ip: str, device_id, login: str, password: str):
        hashed_password = self.hash_password(password)
        user = self.get_user(user_ip, login, hashed_password)
        
        if not user:
            with self.lock_manager.get_lock('register'): user, device_id = self.register(user_ip, login, password, hashed_password)
       
        else:
            session_id = None
            
            if device_id:
                for session in user['sessions']:
                    if session['session_id'] != '' and session['session_id'].split('_')[1] == device_id:
                        session_id = f'{user_ip}_{device_id}'
                        
                        if session['session_id'] == session_id: raise Exception('Device active.')
                        
                        break
            
            if not session_id:
                device_id = self.generate_device_id(user_ip)
                session_id = f'{user_ip}_{device_id}'
            
            self.data['sessions'][session_id] = user['user_id']
            user['sessions'].insert(0, {'session_id': session_id, 'time': int(time())})
            
            while len(user['sessions']) > 5:
                session = user['sessions'].pop(5)
                
                if session['session_id'] != '':
                    del self.data['sessions'][session['session_id']]
            
            self.clear_sessions(user)
            self.update_user_state(user, True)

        return user, device_id

    def register(self, user_ip: str, login: str | None, password: str | None, hashed_password: str | None):
        if self.check_ip(user_ip): raise Exception('Досягнутий максимум аккаунтів.')
        
        self.check_login(login)
        self.check_password(password)

        cur_time = int(time())
        device_id = self.generate_device_id(user_ip)
        session_id = f'{user_ip}_{device_id}'

        user = {
            'ip': user_ip,
            'login': login,
            'password': hashed_password,
            'sessions': [{'session_id': session_id, 'time': cur_time}],

            'user_id': str(self.data['next_user_id']),
            'level': {
                'level': 1,
                'exp': [0, 100]
            },

            'energy': {
                'count': 10,
                'time': None
            },

            'season_pos':None,
            'global_pos': None,
            
            'season_score': 0,
            'global_score': 0,
        }

        self.data['next_user_id'] += 1
        
        self.data['users'][user['user_id']] = user
        self.data['sessions'][session_id] = user['user_id']
        self.data['logins'][login.lower()] = user['user_id']
        
        self.add_to_top(user, 0)
        self.reg_ip(user_ip, user)

        return user, device_id

    def check_login(self, login: str | None):
        length = len(login)
        if length < 3 or length > 20: raise Exception('Довжина логіна повинна бути від 3-ох до 20-ти включно символів.')

        if login.count(' ') > 2: raise Exception('В логіні пробілів не може бути більше двох.')
        if login.startswith(' ') or login.endswith(' '): raise Exception('Логін не може починатися чи закінчуватися на пробіл.')
        if '  ' in login: raise Exception('В логіні не може бути два пробіла підряд.')

        llogin = login.lower()
        available_symbols = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюяabcdefghijklmnopqrstuvwxyz0123456789 '
        for l in llogin:
            if l not in available_symbols: raise Exception(f'В логіні наявний недопустимий символ: " {l} ".')

    def check_password(self, password: str | None):
        length = len(password)
        if length < 6 or length > 20: raise Exception('Довжина пароля повинна бути від 6-ти до 20-ти включно символів.')

    def hash_password(self, password): return sha256(password.encode()).hexdigest()
