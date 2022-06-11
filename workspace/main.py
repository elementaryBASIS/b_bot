#!/usr/bin/env python3

import telebot
from telebot import types
import time, threading, schedule
from config import *
import dialogs

if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)