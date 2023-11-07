import dotenv
import os
import telebot
from llm_handler import Giga
from db import DB
from db_manager import DBManager
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
        self.db = DBManager(self.db_path)

        def gen_markup():
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(telebot.types.InlineKeyboardButton("👍", callback_data="like"),
                                    telebot.types.InlineKeyboardButton("👎", callback_data="dislike"))
            return markup

        @self.bot.message_handler(commands=["start"])
        def start(message, res=False):
            response = config['DEFAULT']['greeting']
            self.bot.send_message(
                message.chat.id, response)
            self.db.log_message(message, response)


        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            response = config['DEFAULT']['error_response']
            try:
                response = self.llmh.call(message.text)
            except Exception as e:
                pass
            self.bot.reply_to(message, response, reply_markup=gen_markup())
            self.db.log_message(message, response)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.data=="like":
                like = 1
            elif call.data=="dislike":
                like = -1
            else:
                like = 0
            self.db.log_like(call.message.id, call.message.chat.id, like)
            self.bot.answer_callback_query(call.id, "Спасибо за оценку!")

    

    def run(self):
        print('bot is pooling')
        self.bot.polling(none_stop=True, interval=1)


if __name__ == '__main__':
    # Запускаем бота
    bot = DtaasHelper()
    bot.run()
