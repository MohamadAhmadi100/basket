import os
from datetime import datetime
import sys
import logging
from logging.handlers import RotatingFileHandler


class LogHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        LogHandler.log_folder_create()
        self.start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        super().__init__(*args, **kwargs)

    @staticmethod
    def log_folder_create():
        if not os.path.exists("log"):
            os.mkdir("log")

    def doRollover(self):
        name = f'{self.start_time} till {datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log'
        self.rotate(self.baseFilename, f"log/{name}")
        self.start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        super().doRollover()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        LogHandler(
            f"log/debug.log",
            mode='a',
            maxBytes=250000
        )
    ]
)


def connection_log(host, port, headers):
    sys.stdout.write("\033[0;32m")
    print(" [x] Consumer running on host \"" + host + ":" + str(port) + "\" , "
          + "headers : " + str(headers), end="")
    sys.stdout.write("\033[1;36m")
    print(" -- Waiting for Requests ...")


def action_log(message, app_name):
    sys.stdout.write("\033[1;31m")
    print("\n => Entry action: ", end="")
    sys.stdout.write("\033[;1m\033[1;34m")
    logging.info(f"Entry action: {message.get(app_name).get('action')}")
    print(message.get(app_name).get("action"))


def request_log(message, app_name):
    sys.stdout.write("\033[1;31m")
    print("                  Request:  ", end="")
    sys.stdout.write("\033[;1m\033[1;34m")
    logging.info(f"Request: {message.get(app_name).get('body')}")
    print(message.get(app_name).get("body"))


def response_log(message):
    sys.stdout.write("\033[1;31m")
    print("                  Responce: ", end="")
    sys.stdout.write("\033[;1m\033[1;34m")
    logging.info(f"Response: {message}")
    print(message)
