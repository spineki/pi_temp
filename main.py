import telebot
import json
import sys
import threading

def getTemp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
            current_temp = int((int(ftemp.read()) / 1000)*100)/100
            temp = current_temp
        except Exception as e:
            print(str(e))
        return temp

try:

    with open("secrets.json", "r") as file:
        data = json.load(file)

        bot_token = data["bot_token"]

        bot_chatID = data["chat_id"]
except Exception as e:
    print("impossible to load the token and chatID. Are you sure you have a proper secrets.json in the same folder", str(e))
    sys.exit(1)

try:
    bot = telebot.TeleBot(bot_token)
except Exception as e:
    print("impossible ti initiate a bot from the bot token. ", str(e))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Hi! type /temp to get the temp, /recap to get a recap, /stop to stop the programm on the raspberry")

@bot.message_handler(commands=['stop', "exit", "shutdown"])
def exit(message):
    bot.reply_to(message, "Bye!")
    print("find du pooling")
    exit(0)

@bot.message_handler(commands=["temp"])
def get_temp(message):
    temp = getTemp()
    if temp is None:
        bot.reply_to(message, "impossible to get the température from the cpu")
    else:
        bot.reply_to(message, str(temp) + "°C")

print("bot start polling...")
bot.polling(none_stop=False, interval=1, timeout=20)