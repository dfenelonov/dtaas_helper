import dotenv
import os
import telebot
from llm_handler import Giga
from db import DbHandler
import configparser

dotenv.load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
assert(os.environ["GIGACHAT_CREDENTIALS"])
config = configparser.ConfigParser()
config.read('conf/config.conf')


class DtaasHelper:
    def __init__(self):
        self.db_path = config['DEFAULT']['db_path']
        self.prompt = config['DEFAULT']['prompt']
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.llmh = Giga(self.prompt)
        self.db = DbHandler(self.db_path)

        @self.bot.message_handler(commands=["start"])
        def start(message, res=False):
            response = config['DEFAULT']['greeting']
            self.bot.send_message(
                message.chat.id, response)
            self.db.insert_data(message, response)
            self.db.flush()

        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            response = config['DEFAULT']['error_response']
            try:
                response = self.llmh.call(message.text)
            except Exception as e:
                pass
            self.bot.reply_to(message, response)
            self.db.save_message(message, response)
            self.db.flush()

    def run(self):
        print('bot is pooling')
        self.bot.polling(none_stop=True, interval=1)


if __name__ == '__main__':
    # Запускаем бота
    bot = DtaasHelper()
    bot.run()
