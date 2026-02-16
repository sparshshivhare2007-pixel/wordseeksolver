from pymongo import MongoClient
from typing import Dict, Optional, Tuple

class Database:
    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "wordle_solver"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users

    def get_user(self, user_id: int) -> Optional[Dict]:
        return self.users.find_one({"user_id": user_id})

    def save_session(self, user_id: int, session_name: str, chat_id: int):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"session_name": session_name, "chat_id": chat_id}},
            upsert=True
        )

    def get_session(self, user_id: int) -> Tuple[Optional[str], Optional[int]]:
        user = self.get_user(user_id)
        return user.get("session_name"), user.get("chat_id") if user else (None, None)

    def remove_session(self, user_id: int):
        self.users.update_one({"user_id": user_id}, {"$unset": {"session_name": "", "chat_id": ""}})

db = Database()
