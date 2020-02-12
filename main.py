import telebot
import json
import sys
import os
import threading
import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# default values -----------------------------------------------------------------------------------------------------------------------------------------
delay_between_temp_check = 10
last_day = None
frequency = 60//delay_between_temp_check

# creating the bot ---------------------------------------------------------------------------------------------------------------------------------------
try:
    bot = telebot.TeleBot(bot_token)
except Exception as e:
    print("impossible ti initiate a bot from the bot token. ", str(e))

# important functions ------------------------------------------------------------------------------------------------------------------------------------
def getTemp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
            current_temp = int((int(ftemp.read()) / 1000)*100)/100
            temp = current_temp
    except Exception as e:
            print(str(e))
            temp = None
    return temp

def getLogs(current_day):
    try:
        logs = ""
        with open("logs/" + current_day, "r") as file:
            for ligne in file:
                logs += ligne + "\n"
        return logs
    except:
        return None

# getting the secrets ------------------------------------------------------------------------------------------------------------------------------------
try:

    with open("secrets.json", "r") as file:
        data = json.load(file)

        bot_token = data["bot_token"]

        bot_chatID = data["chat_id"]
except Exception as e:
    print("impossible to load the token and chatID. Are you sure you have a proper secrets.json in the same folder", str(e))
    sys.exit(1)

# COMMANDS -----------------------------------------------------------------------------------------------------------------------------------------------
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

    logs = getLogs(current_day)

    if logs is not None:
        bot.reply_to(message, "here are the logs\n" + logs)
    else:
        print(str(e))
        bot.reply_to(message, "impossible to get the logs from " + current_day)

def send_graph(logs):
    plt.clf()
    dico = {}
    lignes = logs.split("\n")
    for ligne in lignes:
        try:
            tab = ligne.split()
            dico[tab[0]] = tab[1]
        except: pass

    X = list(dico)
    Y = [dico[k] for k in X]
    my_xticks = list(dico)
    plt.plot(X, Y)

    plt.xticks(X[::frequency], my_xticks[::frequency])
    plt.tick_params(axis="x", labelrotation=-60, labelsize = 12)
    plt.tight_layout()
    plt.savefig("graph/graph.png")
    photo = open("graph/graph.png", "rb")
    bot.send_photo(bot_chatID, photo)

@bot.message_handler(commands = ["graph"])
def get_graph(message, current_day = None):
    global bot_chatID
    print("début du graphe")

    if current_day is not None:
        d = datetime.datetime.today()
        current_day = d.strftime("%d-%m-%Y")
    logs = getLogs(current_day)

    if logs is not None:
        try:
            send_graph(logs)
        except:
            bot.reply_to(message, "unable to retrieve the logs from" + current_day)
    else:
        bot.reply_to(message, "unable to retrieve the logs from" + current_day)

# Creating the folders -----------------------------------------------------------------------------------------------------------------------------------
if not os.path.exists('logs'):
    os.makedirs('logs')

if not os.path.exists('graph'):
    os.makedirs('graph')

# Lauching the bot ---------------------------------------------------------------------------------------------------------------------------------------
bot.send_message(bot_chatID, "Awaken!!!")
print("bot start polling...")

# Launching the background thread ------------------------------------------------------------------------------------------------------------------------
def metricsPolling():
    global last_day
    while True:
        current_temp = getTemp()

        d = datetime.datetime.today()
        current_day  = d.strftime("%d-%m-%Y")
        current_hour = d.strftime("%H:%M:%S")
        if current_day != last_day:
            logs = getLogs(last_day)
            if logs is not None:
                send_graph(logs)
            last_day = current_day
            bot.send_message(bot_chatID, "hey, I'm still awake!")


        with open("logs/"+last_day, "a+") as file:
            file.write(current_hour + " " + str(current_temp) + "\n")

        time.sleep(delay_between_temp_check)

x = threading.Thread(target = metricsPolling , daemon=True)
x.start()





bot.polling(none_stop=False, interval=2, timeout=20)
