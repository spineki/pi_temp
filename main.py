#!/usr/bin/python3

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
    print("💥 impossible to initiate a bot from the bot token.")
    print(str(e))
    exit()

# Lauching the bot ---------------------------------------------------------------------------------------------------------------------------------------
bot.send_message(mp.bot_chatID, "⚙️ Awaken!!! on " + mp.device_name)

print("⚙️ bot start polling on " + mp.device_name )

# display current ip on startup
bot.send_message(mp.bot_chatID, "Current IP:\n" + mp.ip)


available_commands ="""
        Available commands:
        
        - !start, !help: Display the list of available commands
        - !stop, !exit, !shutdown: Stop this program on the pi (but not the pi itself)
        - !temp: Display the current temperature
        - !logs, !log: Display the today logs
        - !mark, !stamp, !event: register this current moment in the logs and add a vertical red line in the plots.
        - !graph: Display a graph of today temperature 
"""

bot.send_message(mp.bot_chatID, available_commands)

# COMMANDS -----------------------------------------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    help_text = """Hello! This bots aim to monitor temperature.
    
    {0}

    Coded by Spineki (Antoine Marras)    
    """.format(available_commands)

    bot.reply_to(message, help_text)

@bot.message_handler(commands=["temp"])
def get_temp(message):
    temperature = mp.getTemp()
    if temperature is None:
        bot.reply_to(message, "impossible to get the température from the cpu")
    else:

        temperature_text = ""
        
        if temperature < 60:
            temperature_text = "❄️ {0}°C".format(str(temperature))
        elif temperature < 80:
            temperature_text = "🔥 {0}°C".format(str(temperature))
        else:
            temperature_text = "💥 {0}°C".format(str(temperature))
        

        if temperature >= mp.warning_temperature:
            temperature_text += "\n⚠️ Careful, the temperature exceed your threshold: " + str(mp.warning_temperature)
        
        bot.reply_to(message, temperature_text)

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
def saveEvent(message):
    if mp.saveEvent():
        bot.reply_to(message, "✔️ event saved in logs")
    else:
        bot.reply_to(message, "❌ fail to save the event!")

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

    bot.reply_to(message, "creating the graph...")

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

@bot.message_handler(commands=['stop', "exit", "shutdown"])
def exit(message):
    bot.reply_to(message, "Bye! ")
    print("Pooling ends")
    exit(0)


# Launching the background thread ------------------------------------------------------------------------------------------------------------------------
mp.metricsPolling()  # Metric pooler, creation of logs...
bot.polling(none_stop=False, interval=2, timeout=20)  # telebot bot. 
