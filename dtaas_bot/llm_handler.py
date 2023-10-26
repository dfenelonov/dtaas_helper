import os
os.environ['GIGACHAT_CREDENTIALS'] = ...

from langchain.llms import GigaChat
from langchain.schema import SystemMessage, HumanMessage

class Giga:
    def __init__(self):
        self._llm = GigaChat(verify_ssl_certs=False)

    def call(self, message):
        messages = [
            SystemMessage(
                content="You are a helpful AI that shares everything you know. Talk in English."
            ),
            HumanMessage(
                content=message
            ),
        ]

        response = self._llm(messages).content
        return response


        