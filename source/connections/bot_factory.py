import telebot

from source.config import BOT_TOKEN

# Central place to build the bot instance.
# Keep it importable from anywhere without side effects.
bot = telebot.TeleBot(BOT_TOKEN)
