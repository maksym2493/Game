from .Game import *
from flask import Flask, abort, request, make_response

game = Game()
lock_manager = game.data_class.lock_manager

site_path = 'Site/'

app = Flask(__name__)

import os
import datetime

def get_last_modified_time(filepath):
    timestamp = os.path.getmtime(filepath)
    last_modified_time = datetime.datetime.utcfromtimestamp(timestamp)
    
    return last_modified_time

scripts = [
    'Client.js',
    'GameTable.js',
    'LoginTable.js',
    'MainGameTable.js',
    'MenuTable.js',
    'ProfileTable.js',
    'SettingsTable.js',
    'Storage.js',
    'TopTable.js',
]

@app.after_request
def add_headers(response):
    if request.path != '/' and not request.path.startswith('/api'):
        response.headers['Cache-Control'] = 'max-age=604800'
    
    if request.path.startswith('/scripts/'):
        response.headers['Content-Type'] = 'application/javascript'
    
    return response

@app.before_request
def before_request():
    public_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    return
    with lock_manager.get_lock(public_ip):
        if not request.path.startswith('/api'):
            if game.security.check_web(request.headers.get('X-Forwarded-For', request.remote_addr)): return abort(403)
        
        else:
            if game.security.check_api(request.headers.get('X-Forwarded-For', request.remote_addr)): return {'status': 'error', 'error': 403}

@app.route('/')
def home():
    last_modified_time = get_last_modified_time(f'{site_path}main.html')
    
    if 'If-Modified-Since' in request.headers: if_modified_since = int(datetime.datetime.strptime(request.headers['If-Modified-Since'], '%a, %d %b %Y %H:%M:%S GMT').timestamp())
    else: if_modified_since = 0
    
    need_update = False
    cached_times = []
    for i, script in enumerate(scripts):
        cached_time = int(get_last_modified_time(f'{site_path}scripts/{script}').timestamp())
        cached_times.append(cached_time)
        
        if cached_time > if_modified_since: need_update = True
    
    if not need_update and if_modified_since >= int(last_modified_time.timestamp()): return make_response('', 304)

    index = open(f'{site_path}main.html', 'r', encoding = 'utf-8').read()
    for i, v in enumerate(cached_times): index = index.replace(f'<<<{i + 1}>>>', str(v))
    
    response = make_response(index)
    response.headers['Last-Modified'] = last_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response

@app.route('/images/<image>')
def get_image(image):
    try: return open(f'{site_path}images/{image}', 'rb').read()
    except: abort(404)

@app.route('/scripts/<script>')
def get_script(script):
    try: return open(f'{site_path}scripts/{script}', 'r', encoding = 'utf-8').read()
    except: abort(404)

@app.route('/api/login')
def login():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 3, ['login', 'password'], ['device_id'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'login', request.args.get('device_id'), **kwargs)}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/logout')
def logout():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 1, ['device_id'])

    try: game.main(user_ip, 'logout', **kwargs); return {'status': 'OK'}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/get_profile')
def get_me():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 2, ['device_id'], ['user_id', 'first_time'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'get_profile', **kwargs, user_id = request.args.get('user_id'), first_time = request.args.get('first_time')) }
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/change_login')
def change_login():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 2, ['device_id', 'login'])

    try: game.main(user_ip, 'change_login', **kwargs); return {'status': 'OK'}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/change_password')
def change_password():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 4, ['device_id', 'old_password', 'new_password', 'repeated_password'])

    try: game.main(user_ip, 'change_password', **kwargs); return {'status': 'OK'}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/get_season_top')
def get_season_top():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 2, ['device_id'], ['page'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'get_season_top', **kwargs, page = request.args.get('page'))}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/get_global_top')
def get_global_top():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 2, ['device_id'], ['page'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'get_global_top', **kwargs, page = request.args.get('page'))}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/reset_sessions')
def remove_session():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 1, ['device_id'])
    
    try: game.main(user_ip, 'reset_sessions', **kwargs); return {'status': 'OK'}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/start_game')
def start_game():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 1, ['device_id'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'start_game', **kwargs)}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/open_cell')
def open_cell():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 3, ['device_id', 'i', 'j'])
    
    try: return {'status': 'OK', 'result': game.main(user_ip, 'open_cell', **kwargs)}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

@app.route('/api/mark_cell')
def mark_cell():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    kwargs = get_kwargs(request.args, 3, ['device_id', 'i', 'j'])
    
    try: game.main(user_ip, 'mark_cell', **kwargs); return {'status': 'OK'}
    except Exception as e: return {"status": "Error", 'error': f'{e.args[0]}'}

def get_kwargs(user_args, max_length, args1, args2 = []):
    kwargs = {}
    if max_length < len(user_args): abort(400)
    
    for arg in args1:
        value = user_args.get(arg)
        if not value: abort(400)
        
        kwargs[arg] = value
    
    for arg in user_args:
        if arg not in args1 and arg not in args2: abort(400)
    
    return kwargs