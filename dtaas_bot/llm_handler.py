from langchain.chat_models import GigaChat
from langchain.schema import SystemMessage, HumanMessage

class Giga():
    def __init__(self):
        self._llm = GigaChat(verify_ssl_certs=False)

    def call(self, message):
        messages = [
            SystemMessage(
                content="Ты полезный помощник по цифровой трансформации. Если не знаешь ответа на запрос пользователя, так и скажи, не фантазируй. Отвечай на русском"
            ),
            HumanMessage(
                content=message
            ),
        ]
        response = self._llm(messages).content
        return response


        