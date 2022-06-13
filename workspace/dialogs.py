import queue
from tabnanny import check
from matplotlib import use
import telebot
from telebot import types
from config import *
from db_requests import *
from random import randint, choice
import datetime

@bot.message_handler(commands=['start'])
def handle_start(m):
    # initalize user record in MongoDB

    cid = m.chat.id
    uid = m.from_user.id
    date = m.date
    if was_user(cid) + is_user(cid):
        db.users.update_one({"_id": str(cid)}, {"$set": {"active": True}})
        bot.send_message(cid, "Мы уже знакомы, если ты хочешь перезапустить ассистента, используй /stop")
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
            "course_length" : 0,
            "day" : "",
            "time" : "",
            "future_question" : "",
            "future_answer" : "",
            "days_gone" : 0,
            "motivation" : 0.7,
            "competition" : 0,
            "passed_lessons" : 0,
            "Neto_state" : 0
        })
        send_next_message(uid)

@bot.message_handler(commands=['stop'])
def stop(m):
    # clear user record

    print("delete from base")
    cid = m.chat.id
    db.users.find_one_and_delete({"_id":str(cid)})

@bot.message_handler(commands=['reflections'])
def get_reflections(m):
    # show reflections statistics

    cid = m.chat.id
    bot.send_message(cid, "Вот все твои рефлексии:")
    for i in ref_db.users.find({"cid":str(cid)}):
       bot.send_message(cid, i["datetime"].strftime("%m/%d/%Y, %H:%M:\nВопрос: ") + i["question"] + "\nТвой ответ: "+ i["text"])

@bot.message_handler(commands=['skip_day'])
def skip_day(m):
    # go to next day, only for testing

    cid = m.chat.id
    bot.send_message(cid, f"\"Debug msg:\" Вы перешли на день вперед, сейчас день {str(db.users.find_one(str(cid))['days_gone'])}")
    day = increment_day(cid)
    if day == 1 or len(db.users.find_one(str(cid))['future_question']) < 5:
        db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "variant_2"}})
    elif day in (2, 5, 7, 9, 10, 15, 18, 20, 29, 30):
        db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "variant_4"}})
    else:
        db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "variant_3"}})
    send_next_message(cid)

@bot.message_handler(commands=['data'])
def get_reflections(m):
    # print saved data from MongoDB

    cid = m.chat.id
    bot.send_message(cid, "Вот все что я знаю о тебе:\n" + str(db.users.find_one(str(cid))))

def question_table(cid):
    # link context and stages to questions from "question_base"

    return {
        "personal_form": { # basic questions only
            0 : basic_questions["get_id"],
            1 : basic_questions["check_profile"],
            2 : basic_questions["course_length"],
            3 : basic_questions["lessons_days"],
            4 : basic_questions["preffered_time"],
            5 : basic_questions["default"]
        },
        "variant_4": { # blocks: 1, 3, 5
            0 : choice(list(notification_questions.values())),
            1 : select_question_group_3(cid, repeat_questions),
            2 : choice(list(bye_question.values())),
        },
        "variant_3": { # everyday questions, blocks: 1, 4, 5
            0 : choice(list(notification_questions.values())),
            1 : pipeline_questions["introduction"],
            2 : pipeline_questions["general_questions"]["question1"],
            3 : pipeline_questions["general_questions"]["question2"],
            4 : pipeline_questions["general_questions"]["question3"],
            5 : pipeline_questions["general_questions"]["question4"],
            6 : pipeline_questions["general_questions"]["question5"],
            7 : choice(list(bye_question.values()))
        },
        "variant_2": { # blocks: 1, 2, 5
            0 : choice(list(notification_questions.values())),
            1 : reflection_questions["lesson_check"],
            2 : reflection_questions["lesson_theme"],
            3 : reflection_questions["lesson_problem_decision"],
            4 : reflection_questions["lesson_problem"],
            5 : reflection_questions["lesson_answer"],
            6 : choice(list(bye_question.values())),
        }
    }
def select_question_group_3(cid, questions):
    # third group is genuine, use specific choice method

    day = db.users.find_one(str(cid))['days_gone']
    if day == 2:
        return questions["questions_first_group"]["question1"]
    elif day <= 7:
        return questions["questions_first_group"][choice(("question2", "question3"))]
    elif day <= 15:
        return questions["questions_first_group"]["question4"]
    elif day == 30:
        return questions["questions_first_group"]["question5"]

def send_next_message(cid):
    # looks at stage, if there's any more, passes it to send_message. May configeure formated answers

    context, stage = get_context(cid)
    try:
        add_data = {
            "personal_form": {
                1 : get_netologic_data(cid).values()
            },
            "variant_4": {
            1 : [db.users.find_one(str(cid))['future_question']]
        },
        }[context][stage]
        
    except KeyError as e:
        add_data = []
    try:
        question = question_table(cid)[context][stage]
    except KeyError as e:
        print("error1", e, context, stage)
        reset_context_and_stage(cid)
    else:
        send_question(cid, question, add_data)


@bot.message_handler(content_types="text")
def process_answer(m):
    # process users answers. Validates input and calls own action callback

    cid = m.chat.id
    context, stage = get_context(cid)
    # lets validate input, if returned None, its ok. If there is error in input, it returns error message
    try:
        question = question_table(cid)[context][stage]
    except KeyError:
        print("No active questions")
        return
    else:
        def validator_mock(text):
            pass
        if "resp_type" in question.keys():
            validate = {
            "" : validator_mock,
            "str": validator_mock,
            "int" : lambda msg : None if msg.isdigit() else "Нет уж. Хочу число!",
            "list" : validator_mock,
            "composite" : validator_mock
            #"list" : lambda msg : None if msg in question["answers_list"] else "Выберите вариант из: " + str(question["answers_list"]),
            #"composite" : lambda msg : None if msg in list(question["answers_list"].keys()) else "Выберите вариант из: " + str(list(question["answers_list"].keys())),
            }[question["resp_type"].lower()](m.text)
            if not validate is None:
                bot.send_message(cid, validate)
                return
    try:
        # if resp_type == None, send next message
        answert_processor = {
            "personal_form" : {
                0 : _personal_form_0_action,
                1 : _personal_form_1_action,
                2 : _personal_form_2_action,
                3 : _personal_form_3_action,
                4 : _personal_form_4_action
            },
            "variant_4" : {
                1 : _variant4_0_action,
            },
            "variant_2" : {
                1 : _variant2_1_action,
                2 : _variant2_2_action,
                3 : _variant2_3_action,
                4 : _variant2_4_action,
                5 : _variant2_5_action
            },
            "variant_3" : {
                2 : _variant3_2_action,
                3 : _variant3_3_action,
                4 : _variant3_4_action,
                5 : _variant3_5_action,
                6 : _variant3_6_action
            }
        }[context][stage]
        answert_processor(cid, m.text, question)
    except KeyError as e:
        print("error2", e, context, stage)
        reset_context_and_stage(cid)
    else:
        send_next_message(cid)

def send_question(cid, question, format_string = []):
    # sends message to user, formats answers. If reply not required, increments stage

    text = question['body'].format(*format_string)
    
    if "answers_list" in question.keys():
        user_markup = types.ReplyKeyboardMarkup(True, True)
        for i in question["answers_list"]:
            user_markup.row(i)
        bot.send_message(cid, text, reply_markup=user_markup)
    else:
        bot.send_message(cid, text)
    if question["resp_type"].lower() == "none":
        increment_stage(cid)
        send_next_message(cid)

def choose_Neto(cid):
    length = int(db.users.find_one(str(cid))["course_length"])
    motiv = db.users.find_one(str(cid))["motivation"]
    passed = db.users.find_one(str(cid))["passed_lessons"]
    if length == 0:
        length = 1
    comp = passed / length
    state = 0
    if (comp < 0.5 and motiv >= 0):
        state = 1
    elif (comp < 0.5 and motiv < 0):
        state = 2
    elif (comp >= 0.5 and motiv < 0):
        state = 3
    elif (comp >= 0.5 and motiv >= 0):
        state = 4

    state_Neto = int(comp * 4)
    db.users.update_one({"_id": str(cid)}, {"$set": {"Neto_state": state_Neto}})
    return state_Neto

    

        
    
# actions' callbacks

def _variant4_0_action(cid, msg, question):
    if msg == question["answers_list"][0]:
        bot.send_message(cid, choice(list(repeat_questions["answers_first_yes"].values()))["body"])
    elif msg == question["answers_list"][1]:
        bot.send_message(cid, choice(list(repeat_questions["answers_first_no"].values()))["body"])
    increment_stage(cid)

def _personal_form_0_action(cid, netologic_id, _question):
    update_netoligic_data(cid, netologic_id)
    print("updated netologic data")
    increment_stage(cid)

def _personal_form_1_action(cid, msg, question):
    #if msg in ["Да, все понятно)","Да, хорошо помню тему)","До сих пор ориентируюсь в этой теме)","Даже спустя время я могу воспроизвести материал!","Да, я до сих пор помню вещи оттуда!"]:
    if msg == question["answers_list"][0]:
        increment_stage(cid)
    #elif msg in ["Чувствую, что понял(а) тему не до конца(", "Если честно уже начинаю забывать(","Теория уже потихоньку уходит из головы(", "Если честно, уже нет :(", "Спустя время я почти все забыл("]:
    elif msg == question["answers_list"][1]:
        bot.send_message(cid, "Жаль, введите верный Netologic ID")
        db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "personal_form"}})
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
    # send_next_message(cid)

def _personal_form_2_action(cid, length, _question):
    db.users.update_one({"_id": str(cid)}, {"$set": {"course_length": length}})
    increment_stage(cid)

def _personal_form_3_action(cid, day, _question):
    db.users.update_one({"_id": str(cid)}, {"$set": {"day": day}})
    increment_stage(cid)

def _personal_form_4_action(cid, time, _question):
    db.users.update_one({"_id": str(cid)}, {"$set": {"time": time}})
    bot.send_message(cid, "На этом закончим")
    increment_stage(cid)

def _variant2_1_action(cid, msg, question):
    if msg == question["answers_list"][0]:
        bot.send_message(cid, "Замечательно, идем дальше")
        increment_stage(cid)
    elif msg == question["answers_list"][1]:
        bot.send_message(cid, "Жаль, что так вышло")
        reset_context_and_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")

def _variant2_2_action(cid, msg, question):
    db.users.update_one({"_id": str(cid)}, {"$set": {"future_question": msg}})
    ref_db.users.insert_one({
            "cid": str(cid),
            "question" : question["body"],
            "text" : msg,
            "datetime" : datetime.datetime.now()
        })
    increment_stage(cid)

def _variant2_3_action(cid, msg, question):
    if msg == question["answers_list"][0]:
        increment_progress(cid)
        increment_stage(cid)
    elif msg == question["answers_list"][1]:
        bot.send_message(cid, "Жаль, что так вышло")
        reset_context_and_stage(cid) 
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")

def _variant2_4_action(cid, msg, question):
    db.users.update_one({"_id": str(cid)}, {"$set": {"future_answer": msg}})
    ref_db.users.insert_one({
            "cid": str(cid),
            "question" : question["body"],
            "text" : msg,
            "datetime" : datetime.datetime.now()
        }) 
    increment_stage(cid)

def _variant2_5_action(cid, msg, question):
    ref_db.users.insert_one({
            "cid": str(cid),
            "question" : question["body"],
            "text" : msg,
            "datetime" : datetime.datetime.now()
        })
    increment_stage(cid)

def _variant3_2_action(cid, msg, question):
    if msg.lower() == "да":
        plus_motivation(cid, 0.05)
        increment_stage(cid)
    elif msg.lower() == "нет":
        plus_motivation(cid, -0.05)
        increment_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
def _variant3_3_action(cid, msg, question):
    if msg.lower() == "да":
        plus_motivation(cid, 0.07)
        increment_stage(cid)
    elif msg.lower() == "нет":
        plus_motivation(cid, -0.07)
        increment_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
def _variant3_4_action(cid, msg, question):
    if msg.lower() == "да":
        plus_motivation(cid, 0.04)
        increment_stage(cid)
    elif msg.lower() == "нет":
        plus_motivation(cid, -0.04)
        increment_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
def _variant3_5_action(cid, msg, question):
    if msg.lower() == "да":
        plus_motivation(cid, 0.06)
        increment_stage(cid)
    elif msg.lower() == "нет":
        plus_motivation(cid, -0.06)
        increment_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
def _variant3_6_action(cid, msg, question):
    if msg.lower() == "да":
        plus_motivation(cid, 0.04)
        increment_stage(cid)
    elif msg.lower() == "нет":
        plus_motivation(cid, -0.04)
        increment_stage(cid)
    else:
        bot.send_message(cid, "Не совсем тебя понимаю")
    
    img = open("neto_pics/" + str(choose_Neto(cid) + 1) + ".gif", 'rb')
    bot.send_photo(cid, img, caption="Твой Нето повзрослел благодаря твоим успехам  обучении! Продолжай в том же духе! :)")

def mock_action(cid, text, _question):
    pass

if __name__ == "__main__":
    bot.polling()