import shelve
from dataclasses import dataclass

from config import DB_NAME, DEBUG

DEFAULT_USER_LEVEL = 4
if DEBUG:
   storage = shelve.open(DB_NAME, writeback=True, flag='n')
   storage.clear()
else:
   storage = shelve.open(DB_NAME, writeback=True)

@dataclass
class User:
   mode: str = '' # 'bot', 'user', 'duel'
   number: str = ''
   level: int = DEFAULT_USER_LEVEL
   tries: int = 0
   history: tuple = ()
   user_history: tuple = ()
   next_turn: bool = True

   def reset(self, new_number = ''):
      self.number = new_number
      self.history = ()
      self.user_history = ()
      self.tries = 0
      self.next_turn = True

def get_or_create_user(id):
   return storage.get(str(id), User())

def save_user(id, user):
   storage[str(id)] = user

def del_user(id):
   id = str(id)
   if id in storage:
      del storage[id]