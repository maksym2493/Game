from threading import Lock

#Race Condition
class LockManager:
    def __init__(self):
        self.locks = {}
        self.lock = Lock()
    
    def get_lock(self, tag):
        with self.lock:
            lock = self.locks.get(tag)
            
            if not lock:
                lock = {
                    'count': 0,
                    'lock': SubLock(self, tag)
                }
                
                self.locks[tag] = lock
            
            lock['count'] += 1
            
            return lock['lock']
    
    def remove_lock(self, tag):
        with self.lock:
            lock = self.locks.get(tag)
            if not lock: return
            
            lock['count'] -= 1
            if not lock['count']: del self.locks[tag]

class SubLock:
    def __init__(self, lock_manager, tag):
        self.tag = tag
        self.lock = Lock()
        
        self.lock_manager = lock_manager
    
    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()
        self.lock_manager.remove_lock(self.tag)