class List(list):
    def __init__(self, a, *args, **kwargs):
        print(a)
        super().__init__(*args, **kwargs)
    
    def append(self, value):
        print(f'Appened {value}')
        if isinstance(value, dict): value = Dict(self.update, self.delete, self.lock_manager, self.parents, 2, value)
        with self.lock_manager.get_lock('dump'): self.update.append(self.parents)
        super().append(value)
    
    def insert(self, index, value):
        print(f'Insert {value}')
        if isinstance(value, dict): value = Dict(self.update, self.delete, self.lock_manager, self.parents, 2, value)
        with self.lock_manager.get_lock('dump'): self.update.append(self.parents)
        super().insert(index, value)
    
    def remove(self, value):
        print(f'Delete {value}')
        with self.lock_manager.get_lock('dump'): self.delete.append(self.parents)
        super().remove(value)

print(List(1, [1, 2, 3]))