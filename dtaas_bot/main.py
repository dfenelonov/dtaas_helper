import dotenv
import os
import telebot
import configparser

from db_manager import DBManager
from vec_base_manager import VecBaseManager

from llm_handler import Giga

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
        self.sys_message = config['DEFAULT']['sys_message']
        # Инициализируем бота
        self.bot = telebot.TeleBot(BOT_TOKEN)
        # Инициализируем и загружаем векторную базу данных
        with VecBaseManager(self.path_to_data, self.path_to_vectorized_db) as vbm:
            self.vs = vbm.load_base()
        # Инициализируем гигачат
        self.llmh = Giga(self.prompt, self.vs, self.sys_message)

        self.db = DBManager(self.db_path)

        def gen_markup():
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(telebot.types.InlineKeyboardButton("👍", callback_data="like"),
                                    telebot.types.InlineKeyboardButton("👎", callback_data="dislike"))
            return markup

        @self.bot.message_handler(commands=["start"])
        def start(message, res=False):
            response = self.greeting_response
            self.bot.send_message(
                message.chat.id, response)
            self.db.log_message(message, response)

        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            response = self.error_response
            try:
                response = self.llmh.get_response(message.text)
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
        print('bot is pooling...')
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    # Запускаем бота
    bot = DtaasHelper()
    bot.run()
