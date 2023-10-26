import dotenv
import os
import telebot
from base_manager import BaseManager
from llm_handler import Giga

dotenv.load_dotenv()


BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN)
llmh = Giga()


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(
        m.chat.id, "Привет! Я ваш помощник по цифровой трансформации на основе AI. Я только учусь")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot_response = "Что-то пошло не так"
    try:
        bot_response = llmh.call(message)
        if len(bot_response) > 4095:
            for x in range(0, len(bot_response), 4095):
                bot.reply_to(message, text=bot_response[x:x+4095])
        else:
            bot.reply_to(message, text=bot_response)
    except Exception as e:
        pass
    bot.send_message(message.chat.id, bot_response)


if __name__ == '__main__':
    base_manager = BaseManager()
    vs = base_manager.load_base()

    # Запускаем бота
    print("Bot is pooling...")
    bot.polling(none_stop=True, interval=0)
