import dotenv
import os
import telebot
from base_manager import BaseManager

dotenv.load_dotenv()



BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(
        m.chat.id, "Привет! Коллеги загрузили в меня некоторые кейсы цифровой трансформации, и я готов расскзаать о них вам. Просто опишите вашу ситуацию, а я постараюсь найти подходящий кейс из моей базы")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot_response = "Что-то пошло не так"
    try:
        found_cases = base_manager.get_cases(message.text)
        bot_response="Мне удалось найти следующее:"
        for case in found_cases:
            case_text = case.page_content +"\n"
            bot_response += case_text

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
