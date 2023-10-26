import dotenv
import os
import telebot
from llm_handler import Giga

dotenv.load_dotenv()


BOT_TOKEN = os.environ["BOT_TOKEN"]
assert(os.environ["GIGACHAT_CREDENTIALS"])

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
        bot_response = llmh.call(message.text)
    except Exception as e:
        pass
    bot.reply_to(message, bot_response)


if __name__ == '__main__':
    # Запускаем бота
    print("Bot is pooling...")
    bot.polling(none_stop=True, interval=0)
