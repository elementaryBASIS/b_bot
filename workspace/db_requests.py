from config import *

def was_user(cid):
    return db.users.find_one(str(cid)) is not None and db.users.find_one(str(cid))['active'] == False

def is_user(cid):
    return db.users.find_one(str(cid)) is not None and db.users.find_one(str(cid))['active'] == True

def get_context(cid):
    return db.users.find_one(str(cid))['question_context'], db.users.find_one(str(cid))['question_stage']

def update_waiting_answer(cid, question):
    val = question["resp_type"] if "resp_type" in question.keys() else ""
    db.users.update_one({"_id": str(cid)}, {"$set": {"waiting_answer": val}})