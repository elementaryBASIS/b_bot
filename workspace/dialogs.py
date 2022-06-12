from tabnanny import check
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
            "target" : ""
        })

        msg = 'Привет!\nДавай знакомиться\n'
        bot.send_message(uid, msg)
        send_next_message(uid)


@bot.message_handler(commands=['stop'])
def stop(m):
    print("delete from base")
    cid = m.chat.id
    db.users.find_one_and_delete({"_id":str(cid)})

def send_next_message(cid):
    context, stage = get_context(cid)

    # select question dictionary for answer
    try:
        {
            "personal_form": {
                0 : lambda cid : send_question(cid, basic_questions["get_id"]),
                1 : lambda cid : send_question(cid, basic_questions["check_profile"], get_netologic_data(cid).items())
            }
        }[context][stage](cid)
    except KeyError as e:
        print("error1", e, context, stage)
        reset_context_and_stage(cid)

def get_question(context, stage):
    return {
        "personal_form": {
            0 : basic_questions["get_id"],
            1 : basic_questions["check_profile"]
        }
    }[context][stage]

@bot.message_handler(content_types="text")
def process_answer(m):
    cid = m.chat.id
    context, stage = get_context(cid)
    # lets validate input, if returned None, its ok. If there is error in input, it returns error message
    try:
        question = get_question(context, stage)
    except KeyError:
        print("No active questions")
        return
    else:
        if "resp_type" in get_question(context, stage).keys():
            validate = {
            "" : None,
            "str": None,
            "int" : lambda msg : None if msg.isdigit() else "Нет уж. Хочу число!",
            "list" : lambda msg : None if msg in get_question(context, stage)["answers_list"] else "Выберите вариант из: " + str(get_question(context, stage)["answers_list"])
            }[question["resp_type"].lower()](m.text)
            if not validate is None:
                bot.send_message(cid, validate)
                return
    try:
        {
            "personal_form" : {
                    0 : _personal_form_0_action,
                    1 : _personal_form_1_action
            }
        }[context][stage](cid, m.text, question)
    except KeyError as e:
        print("error2", e, context, stage)
        reset_context_and_stage(cid)
    else:
        increment_stage(cid)
        send_next_message(cid)

def send_question(cid, question, format_string = []):
    text = question['body'].format(*format_string)
    if "answers_list" in question.keys():
        user_markup = types.ReplyKeyboardMarkup(True, False)
        print(question["answers_list"])
        user_markup.row(*question["answers_list"]) 
        bot.send_message(cid, text, reply_markup=user_markup)
    else:
        bot.send_message(cid, text)

def _personal_form_0_action(cid, netologic_id, _question):
    update_netoligic_data(cid, netologic_id)
    print("updated netologic data")

def _personal_form_1_action(cid, msg, question):
    if msg == question["answers_list"][0]:
        bot.send_message(cid, "Замечательно, сохраняем")
    elif msg == question["answers_list"][1]:
        bot.send_message(cid, "Жаль, введите верный Netologic ID")

if __name__ == "__main__":
    bot.polling()