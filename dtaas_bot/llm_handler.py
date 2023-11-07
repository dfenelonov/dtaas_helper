from langchain.chat_models import GigaChat
from langchain.schema import SystemMessage, HumanMessage

class Giga():
    def __init__(self, prompt):
        self._llm = GigaChat(verify_ssl_certs=False)
        self.prompt = prompt

    def call(self, message):
        messages = [
            SystemMessage(
                content=self.prompt
            ),
            HumanMessage(
                content=message
            ),
        ]
        response = self._llm(messages).content
        return response


        