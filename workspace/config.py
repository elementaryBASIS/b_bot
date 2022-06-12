# used https://github.com/i32ropie/lol as baseline

import telebot
import json
from pymongo import MongoClient

with open("config.txt", 'r') as token_file:
    TOKEN = token_file.readline()

bot = telebot.TeleBot(TOKEN)
mongo = MongoClient('localhost:27017')
db = mongo.b_bot
ref_db = mongo.b_bot_reflections
basic_questions = json.load(open("questions_base/questions_basic.json"))
notification_questions = json.load(open("questions_base/questions_block1.json"))
reflection_questions = json.load(open("questions_base/questions_block2.json"))
repeat_questions = json.load(open("questions_base/questions_block3.json"))
bye_question = json.load(open("questions_base/questions_block5.json"))