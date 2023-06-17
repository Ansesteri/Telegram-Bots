import random
import shelve
import string

import telebot

from config import BOT_TOKEN, DB_NAME

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
   with shelve.open(DB_NAME) as storage:
      storage[str(message.from_user.id)] = (guessed_number, 0)
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
   try:
      with shelve.open(DB_NAME) as storage:
         guessed_number, tries = storage[str(message.from_user.id)]
      level = len(guessed_number)
      if len(text) == level and text.isnumeric() and len(text) == len(set(text)):
         bulls, cows = get_bulls_cows(text, guessed_number)
         tries += 1
         if bulls != level:
            response = f'Bulls: {bulls} | Cows: {cows} | Tries: {tries}'
            with shelve.open(DB_NAME) as storage:
               storage[str(message.from_user.id)] = (guessed_number, tries)
         else:
            if tries <= 3:
               response = f'You guessed right really fast, only in {tries} tries, do you want to play again?'
               with shelve.open(DB_NAME) as storage:
                  del storage[str(message.from_user.id)]
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
            elif tries >= 4 and tries < 8:
               response = f'You guessed right in {tries} tries, do you want to play again?'
               with shelve.open(DB_NAME) as storage:
                  del storage[str(message.from_user.id)]
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
            elif tries >= 8:
               response = f'You guessed right really slow, it took you {tries} tries, do you want to play again?'
               with shelve.open(DB_NAME) as storage:
                  del storage[str(message.from_user.id)]
               bot.send_message(message.from_user.id, response, reply_markup=get_restart_buttons())
               return
      else:
         response = f'Send {level}-digit number that has unique numbers!'
   except KeyError:
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