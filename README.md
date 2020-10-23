# pi_temp
A python-bot to monitor the temperature of a Raspberry pi or a linux computer.

It uses the telebot python api to communicate with a bot. Thus, you need a fully functionnal telegram bot to use this project features.

_In a future version, the bot part wil be separated from the monitoring part. You would be able to get graphs and logs even if you don't have a bot. The logs and graphs are todays saved in logs and graph folders_

If you want to give a try, clone this repository from your machine.

## 1) Install the requirements
` "python3 -m pip install -r requirements.txt" `

You can create a venv if you prefer to do so.
`pip install virtualenv`
`virtualenv venv`
`source  venv/bin/activate`
`pip install -r requirements.txt`

and when you need 
`deactivate` to quit

## 2) Launch the main.py file once.
This will create all the necessary files and folder for the program. (logs, graph, secrets file and config file)


## 3) Create a telegram bot
You will need a token for your bot. Thus, you need a telegram bot. Go to the botfather webpage https://core.telegram.org/bots and create your bot.
You will retrieve a token. It's the bot_token.

1) Then start chatting with your bot. You need at least one message to retrieve the id.

2) Then enter this url in your favorite browser https://api.telegram.org/bot<API-access-token>/getUpdates?offset=0 Where API-acesss-token is your own bot token.

3) In the chat field, id field is the string you need to retrieve.
4) Copy past it in the secrets.json file and here you go!!



## 4) Create a secrets.json file in the folder and fill it as following (you can copy secrets-example.json)
``` json
{
    "bot_token": "Your bot token",
    "bot_chatID":"Your chat Id"
}
```


## 5) Create a config.json in the folder and fill it as following (you can copy config-example.json).
```json
{
    "delay_between_temp_check": 10,
    "max_number_timestamp_displayed": 20,
    "device_name": "Your device name",
    "warning_temperature": 50
}
```


## 6) Relaunch the main.py file. Normaly, your bot will send you a message saying ``` Awaken!!!```

Everything should be working!!

go to your telegram application:
type```/help```, You should get a list of available commands.
type ```/temp```. You should get the current temp
type ```/graph```. you should get your temperature graph
type ```/logs```. you should get your logs.
type ```/exit```. The programm should stop in your raspberry

Logs are stored day by day in the logs folder.

At midnight, the bot will send a graph recaping what happended the last day. 

If the temperature is higher than ```warning_temperature``` in config file, the bot will warn you.



Have fun!!!
