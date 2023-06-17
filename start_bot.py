import random
import shelve
import string

import telebot

from config import BOT_TOKEN
from user import User, DEFAULT_USER_LEVEL, get_or_create_user, save_user, del_user

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'game'])
def select_level(message):
   response = 'Game "Bulls and Cows"\n' + \
               'Chose level (digit count)'
   bot.send_message(message.from_user.id, response, reply_markup=get_level_buttons())

def get_level_buttons():
   buttons = telebot.types.ReplyKeyboardMarkup(
      one_time_keyboard=True,
      resize_keyboard=True,
   )
   buttons.add('3', '4', '5')
   return buttons

def start_game(message, level):
   digits = [s for s in string.digits]
   guessed_number = ''
   for pos in range(level):
      if pos:
         digit = random.choice(digits)
      else:
         digit = random.choice(digits[1:])
      guessed_number += digit
      digits.remove(digit)
   print(f'{guessed_number} for {message.from_user.username}')
   user = get_or_create_user(message.from_user.id)
   user.level = level
   user.reset(guessed_number)
   save_user(message.from_user.id, user)
   bot.reply_to(message, 'Game "Bulls and Cows"\n' 
                f'I guessed a {level}-digit number, try to guess, {message.from_user.first_name}!')

@bot.message_handler(commands=['help'])
def show_help(message):
   bot.reply_to(message, """
Game "Bulls and Cows"

Game where you need to guess in few attempts number that bot guessed. 
After every try bot will say count of right numbers, numbers that are not in correct place ("cows"), and numbers that are in correct place ("bulls")
""")

@bot.message_handler(content_types=['text'])
def bot_answer(message):
   text = message.text
   user = get_or_create_user(message.from_user.id)
   if user.number:
      if len(text) == user.level and text.isnumeric() and len(text) == len(set(text)):
         bulls, cows = get_bulls_cows(text, user.number)
         user.tries += 1
         if bulls != user.level:
            response = f'Bulls: {bulls} | Cows: {cows} | Tries: {user.tries}'
            save_user(message.from_user.id, user)
         else:
            if user.tries <= 3:
               response = f'You guessed right really fast, only in {user.tries} tries, do you want to play again?'
               user.reset()
               save_user(message.from_user.id, user)
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
            elif user.tries >= 4 and user.tries < 8:
               response = f'You guessed right in {user.tries} tries, do you want to play again?'
               user.reset()
               save_user(message.from_user.id, user)
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
            elif user.tries >= 8:
               response = f'You guessed right really slow, it took you {user.tries} tries, do you want to play again?'
               user.reset()
               save_user(message.from_user.id, user)
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
      else:
         response = f'Send {user.level}-digit number that has unique numbers!'
   else:
      if text in ('3', '4', '5'):
         start_game(message, int(text))
         return
      elif text == 'Yes':
         select_level(message)
         return
      else:
         response =  'To start the game write /start'
   bot.send_message(message.from_user.id, response)

def get_restart_buttons():
   buttons = telebot.types.ReplyKeyboardMarkup(
      one_time_keyboard=True,
      resize_keyboard=True,
   )
   buttons.add('Yes', 'No')
   return buttons

def get_bulls_cows(text1, text2):
   bulls = cows = 0
   for i in range(min(len(text1), len(text2))):
      if text1[i] in text2:
         if text1[i] == text2[i]:
            bulls += 1
         else:
            cows += 1
   return bulls, cows

if __name__ == '__main__':
   print('Bot started!')
   bot.polling(non_stop=True)