# pi_temp
A python-bot to monitor the temperature of a Raspberry pi.
It uses the telebot python api to communicate with a bot. Thus, you need a fully functionnal telegram bot to use this project features.

_In a future version, the bot part wil be separated from the monitoring part. You would be able to get graphs and logs even if you don't have a bot. The logs and graphs are todays saved in logs and graph folders_

If you want to give a try, clone this repository from your raspberry.
Add a file _secrets.json_ in the same folder.

fill this file as following
{
    "bot_token": "Your bot token",
    "chat_id":"Your chat Id"
}

cd to the main folder.
## Install the requirements
type "python3 -m pip install -r requirements.txt"
## Run the main file
type "python3 main.py"

Everything should be working!!

go to your telegram application:
type "/temp". You should get the current temp
type "graph". you should get your temperature graph
type "/exit". The programm should stop in your raspberry
