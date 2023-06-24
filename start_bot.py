import random
import string
from itertools import product

import telebot

from config import BOT_TOKEN
from user import User, DEFAULT_USER_LEVEL, get_or_create_user, save_user, del_user

GAME_MODES = ('Bot', 'User', 'Duel')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['mode'])
def select_mode(message):
   user = get_or_create_user(message.from_user.id)
   user.mode = ''
   user.reset()
   response = 'Game "Bulls and Cows"\n' + \
               'Chose mode (who guesses the number)'
   bot.send_message(message.from_user.id, response, reply_markup=get_buttons(*GAME_MODES))

@bot.message_handler(commands=['level'])
def select_level(message):
   user = get_or_create_user(message.from_user.id)
   user.reset()
   user.level = None
   save_user(message.from_user.id, user)
   response = 'Game "Bulls and Cows"\n' + \
               'Choose level (digit count)'
   bot.send_message(message.from_user.id, response, reply_markup=get_buttons('3', '4', '5'))

@bot.message_handler(commands=['start', 'game'])
def start_game(message, level=None):
   response = 'Game "Bulls and Cows"\n'
   user = get_or_create_user(message.from_user.id)
   if not user.mode:
      select_mode(message)
      return
   if level:
      user.level = level
   if user.mode in ('bot', 'duel'):
      digits = [s for s in string.digits]
      guessed_number = ''
      for pos in range(user.level):
         if pos:
            digit = random.choice(digits)
         else:
            digit = random.choice(digits[1:])
         guessed_number += digit
         digits.remove(digit)
      print(f'{guessed_number} for {message.from_user.username}')
      user.reset(guessed_number)
      save_user(message.from_user.id, user)
      if user.mode == 'bot':
         response += f'I guessed a {user.level}-digit number, try to guess, {message.from_user.first_name}!'
      else:
         response += (f'I guessed a {user.level}-digit number, guess a number too.\n'
         f'Whoever guesses first wins, Your turn {message.from_user.first_name}')
      bot.reply_to(message, response)
   elif user.mode == 'user':
      bot.reply_to(message, 'Game "Bulls and Cows"\n' 
                  f'Guess a {user.level}-digit number, and I will try to guess it and you send me count of bulls and cows, {message.from_user.first_name}!')
      bot_answer_with_guess(message, user)

@bot.message_handler(commands=['help'])
def show_help(message):
   bot.reply_to(message, """
Game "Bulls and Cows"

Game where you need to guess in few attempts number that bot guessed. 
After every try bot will say count of right numbers, numbers that are not in correct place ("cows"), and numbers that are in correct place ("bulls")
""")

@bot.message_handler(content_types=['text'])
def bot_answer(message):
   user = get_or_create_user(message.from_user.id)
   if user.number and (user.mode == 'bot' or (user.mode == 'duel' and user.next_turn)):
      bot_answer_to_user_guess(message, user)
   elif user.level and user.mode == 'user':
      bot_answer_with_guess(message, user)
   elif user.mode == 'duel' and not user.next_turn:
      if bot_has_won(message, user):
         return
      response = ''
      for number, bulls, cows, in user.user_history:
         response = f'{number} | {bulls} bulls | {cows} cows \n'
      response += f'Your turn! ({user.tries+1} try)'
      bot.send_message(message.from_user.id, response)
      user.next_turn = True
      save_user(message.from_user.id, user)
   else:
      bot_answer_not_in_game(message, user)

def bot_answer_not_in_game(message, user):
   text = message.text
   if text in ('3', '4', '5'):
      start_game(message, int(text))
      return
   elif text == 'Yes':
      start_game(message, user.level)
      return
   elif not user.mode and text in GAME_MODES:
      if text == 'Bot':
         user.mode = 'bot'
      elif text == 'User':
         user.mode = 'user'
      elif text == 'Duel':
         user.mode = 'duel'
      save_user(message.from_user.id, user)
      start_game(message, user.level)
      return
   else:
      response =  'To start the game write /start or additionaly choose level with /level'
   bot.send_message(message.from_user.id, response)

def bot_answer_to_user_guess(message, user):
   text = message.text
   if len(text) == user.level and text.isnumeric() and len(text) == len(set(text)):
      bulls, cows = get_bulls_cows(text, user.number)
      history = list(user.user_history)
      history.append((text, bulls, cows))
      user.user_history = tuple(history)
      user.tries += 1
      user.next_turn = False
      if bulls != user.level:
         response = f'Bulls: {bulls} | Cows: {cows} | Tries: {user.tries}'
         save_user(message.from_user.id, user)
         bot.send_message(message.from_user.id, response)
         if user.mode == 'duel':
            bot_answer_with_guess(message, user)
      else:
         if user.tries <= 3:
            response = f'You guessed right really fast, only in {user.tries} tries, do you want to play again?'
            user.reset()
            save_user(message.from_user.id, user)
            bot.send_message(message.from_user.id, response, reply_markup=get_buttons('Yes', 'No'))
         elif user.tries >= 4 and user.tries < 8:
            response = f'You guessed right in {user.tries} tries, do you want to play again?'
            user.reset()
            save_user(message.from_user.id, user)
            bot.send_message(message.from_user.id, response, reply_markup=get_buttons('Yes', 'No'))
         elif user.tries >= 8:
            response = f'You guessed right really slow, it took you {user.tries} tries, do you want to play again?'
            user.reset()
            save_user(message.from_user.id, user)
            bot.send_message(message.from_user.id, response, reply_markup=get_buttons('Yes', 'No'))
   else:
      response = f'Send {user.level}-digit number that has unique numbers!'
      bot.send_message(message.from_user.id, response)

def bot_answer_with_guess(message, user):
   if user.mode == 'user' and bot_has_won(message, user):
      return
   history = list(user.history)
   all_variants = [''.join(x) for x in product(string.digits, repeat=user.level)
                   if len(x) == len(set(x)) and x[0] != '0']
   while all_variants:
      guess = random.choice(all_variants)
      all_variants.remove(guess)
      if is_compatible(guess, history):
         break
   else:
      response = 'Unfortunately, in your answers were mistakes, I don`t have any variants left...)'
      stop_game_with_message(message, user, response)
      return
   history.append((guess, None, None))
   if user.mode == 'user':
      user.tries += 1
   user.history = tuple(history)
   save_user(message.from_user.id, user)
   keys = []
   for bulls in range(user.level + 1):
      for cows in range(user.level + 1 - bulls):
         if bulls != 4:
            keys.append(f'{bulls}-{cows}')
         else:
            keys.append(f'{bulls}-{cows}-Bot won!')
   response = f'My variant is {guess} ({user.tries} try)\n' + \
               'How many bulls and cows I guessed?'
   bot.send_message(message.from_user.id, response, reply_markup=get_buttons(*keys))

def bot_has_won(message, user):
   history = list(user.history)
   if history:
      history[-1] = (history[-1][0], *[int(x) for x in message.text.split('-')[:2]])
      if history[-1][1] == user.level:
         response = f'I won in {user.tries} tries!!!'
         stop_game_with_message(message, user, response)
         return True
      user.history = tuple(history)
      save_user(message.from_user.id, user)
   return False

def stop_game_with_message(message, user, response):
   user.reset()
   save_user(message.from_user.id, user)
   bot.send_message(message.from_user.id, response + '\nSend /start to start new game')

def is_compatible(guess, history):
   return all(get_bulls_cows(guess, previous_guess) == (bulls, cows) 
                for previous_guess, bulls, cows in history)

def get_buttons(*args):
   buttons = telebot.types.ReplyKeyboardMarkup(
      one_time_keyboard=True,
      resize_keyboard=True,
   )
   buttons.add(*args)
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