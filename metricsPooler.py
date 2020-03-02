import json
import os


class MetricsPooler:
    def __init__(self):
        self.logFolder = "logs"
        self.delay_between_temp_check = None
        self.max_number_timestamp_displayed = None
        self.last_day = None
        self.bot_token = None
        self.bot_chatID = None
    
    def checkup(self):
        self.load_pooling_config()
        self.get_secrets()
        self.create_folders()

    def load_pooling_config(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.delay_between_temp_check = data["delay_between_temp_check"]
                self.max_number_timestamp_displayed = data["max_number_timestamp_displayed"]

        except:
            # if an error occured, we recreate the config file
            print("impossible to load the config file")
            self.delay_between_temp_check = 10
            self.max_number_timestamp_displayed = 20

            with open("config.json", "w+") as f:
                data = {
                "delay_between_temp_check": self.delay_between_temp_check,
                "max_number_timestamp_displayed" : self.max_number_timestamp_displayed
                }

                json.dump(data, f, indent = 4)
    
    def get_secrets(self):

        try:
            with open("secrets.json", "r") as file:
                data = json.load(file)
                self.bot_token = data["bot_token"]
                self.bot_chatID = data["bot_chatID"]
    
        except Exception as e:
            print("impossible to load the token and chatID. Make sure too properly write your secrets file", str(e))
    
            with open("secrets.json", "w+") as f:
                data = {
                    "bot_token" : "Your bot token",
                    "bot_chatID" : "your chat id"
                }
                json.dump(data, f, indent = 4) 

    def create_folders(self):

        if not os.path.exists('logs'):
            os.makedirs('logs')

        if not os.path.exists('graph'):
            os.makedirs('graph')

    # important functions ------------------------------------------------------------------------------------------------------------------------------------
    def getTemp(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
                current_temp = int((int(ftemp.read()) / 1000)*100)/100
                temp = current_temp
        except Exception as e:
                print(str(e))
                temp = None
        return temp

    def getLogs(self, current_day):
        try:
            logs = ""
            with open("logs/" + current_day, "r") as file:
                for ligne in file:
                    logs += ligne + "\n"
            return logs
        except:
            return None
