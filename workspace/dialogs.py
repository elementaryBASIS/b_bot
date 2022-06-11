import telebot
from telebot import types
from config import *
from db_requests import *

@bot.message_handler(commands=['start'])
def handle_start(m):
    cid = m.chat.id
    uid = m.from_user.id
    date = m.date
    if was_user(cid) + is_user(cid):
        # db.users.remove(str(cid))
        db.users.update_one({"_id": str(cid)}, {"$set": {"active": True}})
    else:
        db.users.insert_one({
            "_id": str(cid),
            "first_name" : m.from_user.first_name,
            "last_name" : m.from_user.last_name,
            "nickname" : m.from_user.username,
            "netologic_id" : "",
            "active": True,
            "register": date,
            "course_name": None,
            "question_context" : "personal_form",
            "question_stage" : 0,
            "target" : "",
            "waiting_answer" : ""
        })

        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Рандомный вопрос') 
        msg = 'Привет!\nДавай знакомиться\n'
        bot.send_message(uid, msg, reply_markup=user_markup)
        choose_next_message(uid)


@bot.message_handler(commands=['stop'])
def stop(m):
    print("delete from base")
    cid = m.chat.id
    db.users.find_one_and_delete({"_id":str(cid)})

def choose_next_message(uid):
    personal_form = {
        0 : lambda uid : send_question(uid, start_questions["get_id"])
    }
    {
        "personal_form" : lambda uid : 
    }
def send_question(uid, question):
    text = question['body']
    update_waiting_answer(uid, question)
    bot.send_message(uid, text)

