import telebot
import json
import sys


try:

    with open("secrets.json", "r") as file:
        data = json.load(file)

        bot_token = data["bot_token"]

        bot_chatID = data["chat_id"]
except Exception as e:
    print("impossible to load the token and chatID.", str(e))
    sys.exit(1)

try:
    bot = telebot.TeleBot(bot_token)
except Exception as e:
    print("impossible ti initiate a bot from the bot token. ", str(e))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['stop', "exit", "shutdown"])
def exit(message):
    bot.reply_to(message, "Bye!")
    sys.exit(0)



print("bot start polling...")
bot.polling(none_stop=False, interval=1, timeout=20)