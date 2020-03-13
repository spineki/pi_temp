import telebot
import threading
import time
import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, SECONDLY, rrulewrapper, RRuleLocator, MINUTELY

# custom
from metricsPooler import MetricsPooler


# creating the metrics Pooler
mp = MetricsPooler()
mp.checkup() # harvest configuration, folders, etc.



# creating the bot ---------------------------------------------------------------------------------------------------------------------------------------
try:
    bot = telebot.TeleBot(mp.bot_token)
except Exception as e:
    print("impossible ti initiate a bot from the bot token. ", str(e))
    exit()

# Lauching the bot ---------------------------------------------------------------------------------------------------------------------------------------
bot.send_message(mp.bot_chatID, "Awaken!!!")
print("bot start polling...")




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
    temp = mp.getTemp()
    if temp is None:
        bot.reply_to(message, "impossible to get the température from the cpu")
    else:
        bot.reply_to(message, str(temp) + "°C")

@bot.message_handler(commands=["log", "logs"])
def get_logs(message):

    d = datetime.datetime.today()
    current_day = d.strftime("%d-%m-%Y")

    logs = mp.getLogs(current_day)

    if logs is not None:
        bot.reply_to(message, "here are the logs\n" + logs)
    else:
        print(str(e))
        bot.reply_to(message, "impossible to get the logs from " + current_day)

@bot.message_handler(commands = ["mark", "stamp", "event"])
def save_event(message):
    if mp.save_event():
        bot.reply_to(message, "event saved in logs")
    else:
        bot.reply_to(message, "fail to save the event!")

def send_graph(logs):
    plt.clf()

    fig, ax = plt.subplots()

    dico = {}
    events = []
    lignes = logs.split("\n")

    for ligne in lignes:
        try:
            tab = ligne.split()
            if tab[1] == "event":
                events.append(tab[0])
            else:
                dico[tab[0]] = tab[1]
        except: pass

    X = list(dico)
    X = [datetime.datetime.strptime(x,"%H:%M:%S") for x in X]
    Y = [float(dico[elem]) for elem in dico]
    
    plt.plot_date(X, Y, linestyle ="--")
    
    #plt.set_major_formatter(formatter)
    print(events, "event")
    for event in events:
        print(event)
        ax.axvline(x=  datetime.datetime.strptime(event, "%H:%M:%S"), color = "red")
    
    step = len(X)//mp.max_number_timestamp_displayed
    step = max(1, step) # to avoid a 0 step if there is not enought measures

    plt.xticks(ticks = X[::step])
    ax.xaxis.set_tick_params(labelrotation=-60, labelsize = 12)
    formatter = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(formatter)
    plt.tight_layout()

    plt.savefig("graph/graph.png")
    photo = open("graph/graph.png", "rb")
    bot.send_photo(mp.bot_chatID, photo)

@bot.message_handler(commands = ["graph"])
def get_graph(message, current_day = None):
    print("creating the graph")

    if current_day is None:
        d = datetime.datetime.today()
        current_day = d.strftime("%d-%m-%Y")
    logs = mp.getLogs(current_day)

    if logs is not None:
        try:
            send_graph(logs)
        except Exception as e:
            bot.reply_to(message, "unable to retrieve the logs from" + current_day + str(e))
    else:
        bot.reply_to(message, "unable to retrieve the logs from" + current_day)




# Launching the background thread ------------------------------------------------------------------------------------------------------------------------
mp.metricsPolling()  # Metric pooler, creation of logs...
bot.polling(none_stop=False, interval=2, timeout=20)  # telebot bot. 
