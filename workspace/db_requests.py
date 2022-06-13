from random import randint
from config import *

def was_user(cid):
    return db.users.find_one(str(cid)) is not None and db.users.find_one(str(cid))['active'] == False

def is_user(cid):
    return db.users.find_one(str(cid)) is not None and db.users.find_one(str(cid))['active'] == True

def get_context(cid):
    return db.users.find_one(str(cid))['question_context'], db.users.find_one(str(cid))['question_stage']

def increment_stage(cid):
    current_stage = db.users.find_one(str(cid))['question_stage']
    db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": current_stage + 1}})
    return current_stage + 1

def plus_motivation(cid, val):
    current_stage = db.users.find_one(str(cid))['motivation'] + val
    db.users.update_one({"_id": str(cid)}, {"$set": {"motivation": current_stage}})

def reset_context_and_stage(cid):
    db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "default"}})

def update_netoligic_data(cid, netologic_id):
    if int(netologic_id) > 18760:
        netologic_id = randint(2, 18760)
    user_info = dataframe.iloc[int(netologic_id) + 1]
    coursename = user_info["Название программы"]
    target = user_info["Цель обучения"]
    data = {"netologic_id": netologic_id, "course_name": coursename, "target": target}
    db.users.update_one({"_id": str(cid)}, {"$set": data})
    return data

def increment_day(cid):
    day = db.users.find_one(str(cid))['days_gone']
    db.users.update_one({"_id": str(cid)}, {"$set": {"days_gone": day + 1}})
    return day + 1

def get_netologic_data(cid):
    data =  db.users.find_one(str(cid))
    return {"netologic_id": data["netologic_id"], "course_name": data["course_name"], "target": data["target"]}