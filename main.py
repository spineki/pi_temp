import telebot
import json
import sys
import os
import threading
import time
import datetime


# Here are defined some default values
delay_between_temp_check = 10
last_day = None

# we create a logs folder
if not os.path.exists('logs'):
    os.makedirs('logs')

def metricsPolling():
    global last_day
    while True:
        current_temp = getTemp()

        d = datetime.datetime.today()
        current_day = d.strftime("%d-%m-%Y")
        current_hour = d.strftime("%H:%M:%S")
        if current_day is not last_day:
            last_day = current_day


        with open("logs/"+last_day, "a+") as file:
            file.write(current_hour + " " + str(current_temp) + "\n")

        time.sleep(delay_between_temp_check)

def getTemp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
            current_temp = int((int(ftemp.read()) / 1000)*100)/100
            temp = current_temp
    except Exception as e:
            print(str(e))
            temp = None
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

@bot.message_handler(commands=["log", "logs"])
def get_logs(message):

    d = datetime.datetime.today()
    current_day = d.strftime("%d-%m-%Y")

    try:
        logs = ""
        with open("logs/" + current_day, "r") as file:
            for ligne in file:
                logs+=ligne + "°C"
        bot.reply_to(message, "here are the logs\n" + logs)
    except Exception as e:
        print(str(e))
        bot.reply_to(message, "impossible to get the logs from " + current_day)

x = threading.Thread(target = metricsPolling , daemon=True)
x.start()

print("bot start polling...")
bot.polling(none_stop=False, interval=1, timeout=20)
