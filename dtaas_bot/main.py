import dotenv
import os
import configparser
import telebot
from llm_handler import Giga
from db import DbHandler
from conf.config import Configuration
from vec_base_handler import BaseManager



dotenv.load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
assert(os.environ["GIGACHAT_CREDENTIALS"])
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class DtaasHelper:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('conf/config.conf')
        self.db_path = config['DEFAULT']['db_path']
        self.prompt = config['DEFAULT']['prompt']
        self.path_to_data = config['DEFAULT']['path_to_data']
        self.error_response = config['DEFAULT']['error_response']
        self.greeting_response = config['DEFAULT']['error_response']
        self.path_to_vectorized_db = config['DEFAULT']['path_to_vectorized_db']
        self.data_type = config['DEFAULT']['data_type']
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.db = DbHandler(self.db_path)
        self.bm = BaseManager(self.path_to_data, self.path_to_vectorized_db)
        self.vs = self.bm.load_base()
        self.llmh = Giga(self.prompt, self.vs)

        @self.bot.message_handler(commands=["start"])
        def start(message, res=False):
            response = self.greeting_response
            self.bot.send_message(
                message.chat.id, response)
            self.db.save_message(message, response)
            self.db.flush()

        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            response = self.error_response
            try:
                response = self.llmh.get_response(message.text)
            except Exception as e:
                print(str(e))
            self.bot.reply_to(message, response)
            self.db.save_message(message, response)
            self.db.flush()

    def run(self):
        print('bot is pooling...')
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    # Запускаем бота
    bot = DtaasHelper()
    bot.run()
