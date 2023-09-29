import dotenv
import os
import telebot
from base_manager import BaseManager

dotenv.load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN)
base_manager = BaseManager()

@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(
        m.chat.id, "Привет! Коллеги загрузили в меня некоторые кейсы цифровой трансформации, и я готов расскзаать о них вам. Просто опишите вашу ситуацию, а я постараюсь найти подходящий кейс из моей базы")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot_response = "Что-то пошло не так"
    try:
        bot_response = base_manager.get_case(message)
    except:
        pass
    bot.send_message(message.chat.id, bot_response)


if __name__ == '__main__':

    # Запускаем бота
    print("Bot is pooling...")
    bot.polling(none_stop=True, interval=0)
