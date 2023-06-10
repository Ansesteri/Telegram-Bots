import random
import string

import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
guessed_number = ''

@bot.message_handler(commands=['start', 'game'])
def start_game(message):
   digits = [s for s in string.digits]
   global guessed_number
   guessed_number = ''
   for pos in range(4):
      if pos:
         digit = random.choice(digits)
      else:
         digit = random.choice(digits[1:])
      guessed_number += digit
      digits.remove(digit)
   bot.reply_to(message, f'I guessed a 4-digit number, try to guess, {message.from_user.first_name}!')

@bot.message_handler(content_types=['text'])
def bot_answer(message):
   text = message.text
   if len(text) == 4 and text.isnumeric():
      response = text
   else:
      response = 'Send 4-digit number!'
   bot.send_message(message.from_user.id, response)

if __name__ == '__main__':
   print('Bot started!')
   bot.polling(non_stop=True)