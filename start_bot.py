import random
import string

import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
guessed_number = ''
tries = 0

@bot.message_handler(commands=['start', 'game'])
def start_game(message):
   digits = [s for s in string.digits]
   global guessed_number, tries
   guessed_number = ''
   for pos in range(4):
      if pos:
         digit = random.choice(digits)
      else:
         digit = random.choice(digits[1:])
      guessed_number += digit
      digits.remove(digit)
   print(guessed_number)
   tries = 0
   bot.reply_to(message, 'Game "Bulls and Cows"\n' 
                f'I guessed a 4-digit number, try to guess, {message.from_user.first_name}!')

@bot.message_handler(commands=['help'])
def show_help(message):
   bot.reply_to(message, """
Game "Bulls and Cows"

Game where you need to guess in few attempts number that bot guessed. 
Number is 4-digit without repeated numbers in it (ex. : 2139). 
""")

@bot.message_handler(content_types=['text'])
def bot_answer(message):
   text = message.text
   global tries
   if len(text) == 4 and text.isnumeric() and len(text) == len(set(text)):
      tries += 1
      bulls, cows = get_bulls_cows(text, guessed_number)
      if bulls == 4:
         if tries <= 3:
            response = f'You guessed right really fast, only in {tries} tries, you can start new game using /game or /start!'
         elif tries >= 4 and tries < 8:
            response = f'You guessed right in {tries} tries, you can start new game using /game or /start!'
         elif tries >= 8:
            response = f'You guessed right really slow, it took you {tries} tries, you can start new game using /game or /start!'
      else:
         response = f'Bulls: {bulls} | Cows: {cows} | Tries: {tries}'
   else:
      response = 'Send 4-digit number that has unique numbers!'
   bot.send_message(message.from_user.id, response)

def get_bulls_cows(text1, text2):
   bulls = cows = 0
   for i in range(4):
      if text1[i] in text2:
         if text1[i] == text2[i]:
            bulls += 1
         else:
            cows += 1
   return bulls, cows

if __name__ == '__main__':
   print('Bot started!')
   bot.polling(non_stop=True)