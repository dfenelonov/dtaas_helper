import sqlite3
from datetime import datetime
from db import DB


class DBManager:
    def __init__(self, db_path):
        self.db = DB(db_path)
    
    def log_message(self, message, response):
        self.db.save_message( message.message_id, message.from_user.id, message.chat.id, 
                             message.text, response)
        self.db.flush()



   
