import sqlite3
from datetime import datetime

class DB_Handler():
    def __init__(self):
        self.connect = sqlite3.connect("db\\logs.db", check_same_thread=False)
        self.cur = self.connect.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS logs(
                                                            message_id INTEGER PRIMARY KEY,
                                                            user_id INTEGER,
                                                            session_id INTEGER,
                                                            message TEXT,
                                                            response TEXT, 
                                                            dt TEXT,
                                                            like INTEGER
                                                            )
                        """
                        )

    def save_message(self, message, response):
        currentDateAndTime = datetime.now()
        self.cur.execute("INSERT INTO  logs VALUES(?, ?, ?, ?, ?, ?, ?)", (message.message_id, message.from_user.id, message.chat.id, message.text, response, currentDateAndTime, 'like'))
        self.connect.commit()

    def __del__(self):
        self.cursor.close()
        self.connect.close()