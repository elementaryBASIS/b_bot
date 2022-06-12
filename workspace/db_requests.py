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

def reset_context_and_stage(cid):
    db.users.update_one({"_id": str(cid)}, {"$set": {"question_stage": 0, "question_context": "default"}})

def update_netoligic_data(cid, netologic_id):
    user_info = dataframe.iloc[int(netologic_id) + 1]
    coursename = user_info["Название программы"]
    target = user_info["Цель обучения"]
    data = {"netologic_id": netologic_id, "course_name": coursename, "target": target}
    db.users.update_one({"_id": str(cid)}, {"$set": data})
    return data


def get_netologic_data(cid):
    data =  db.users.find_one(str(cid))
    return {"netologic_id": data["netologic_id"], "course_name": data["course_name"], "target": data["target"]}