import shelve
from dataclasses import dataclass

from config import DB_NAME

DEFAULT_USER_LEVEL = 4
storage = shelve.open(DB_NAME, writeback=True)

@dataclass
class User:
    number: str = ''
    level: int = DEFAULT_USER_LEVEL
    tries: int = 0
    def reset(self, new_number = ''):
        self.number = new_number
        self.tries = 0

def get_or_create_user(id):
    return storage.get(str(id), User())

def save_user(id, user):
    storage[str(id)] = user

def del_user(id):
    id = str(id)
    if id in storage:
        del storage[id]