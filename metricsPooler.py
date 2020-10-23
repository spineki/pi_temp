import json
import os
import datetime
import threading
from subprocess import check_output
import time


class MetricsPooler:
    def __init__(self):
        self.logFolder = "logs"
        self.delay_between_temp_check: float = None
        self.max_number_timestamp_displayed: int = None
        self.current_day: str = None
        self.bot_token: str = None
        self.bot_chatID: str = None
        self.ip: str = None
        self.sendMessage = None
        self.bot_ref = None

    def setSendMessageFunction(self, sendMessageFunction):
        self.sendMessage = sendMessageFunction

    
    def checkup(self):
        self._loadPoolingConfig()
        self._loadSecrets()
        self._createFolders()
        self._fetchIp()

    def _loadPoolingConfig(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                self.delay_between_temp_check = data["delay_between_temp_check"]
                self.max_number_timestamp_displayed = data["max_number_timestamp_displayed"]
                self.device_name = data["device_name"]
                self.warning_temperature = data["warning_temperature"]

        except:
            # if an error occured, we recreate the config file
            print("impossible to load the config file")
    
    def _loadSecrets(self):

        try:
            with open("secrets.json", "r") as file:
                data = json.load(file)
                self.bot_token = data["bot_token"]
                self.bot_chatID = data["bot_chatID"]
    
        except Exception as e:
            print("impossible to load the token and chatID. Make sure too properly write your secrets file", str(e))
    
            with open("secrets_example.json", "w+") as f:
                data = {
                    "bot_token" : "Your bot token",
                    "bot_chatID" : "your chat id"
                }
                json.dump(data, f, indent = 4) 

    def _createFolders(self):

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

    def _fetchIp(self):
        local_ip = str(check_output(["hostname", "-I"]))
        self.ip = "\n".join(str(local_ip).strip().split())

    def saveEvent(self):

        try:
            d = datetime.datetime.today()
            self.current_day  = d.strftime("%d-%m-%Y")
            current_hour = d.strftime("%H:%M:%S")

            with open("logs/" + self.current_day, "a+") as file:
                file.write(current_hour + " " + "event" + "\n")
            return True
        except:
            return False

    def metricsPolling(self):

        def _metricsPolling():
            
            while True:
                current_temp = self.getTemp()

                d = datetime.datetime.today()
                self.current_day  = d.strftime("%d-%m-%Y")
                current_hour = d.strftime("%H:%M:%S")


                if (current_temp > self.warning_temperature): # warn the user
                    self.sendMessage("⚠️ Careful, the temperature 🔥{0}°C🔥 exceeds {1}°C".format(str(current_temp), str(self.warning_temperature) ))
                with open("logs/" + self.current_day, "a+") as file:
                    file.write(current_hour + " " + str(current_temp) + "\n")

                time.sleep(self.delay_between_temp_check)
        
        x = threading.Thread(target = _metricsPolling, daemon=True)
        x.start()

