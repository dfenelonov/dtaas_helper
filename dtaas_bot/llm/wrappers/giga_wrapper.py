from .llm_wrapper_interface import LLMWrapperInterface
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import os
import configparser

class GigaWrapper(LLMWrapperInterface):
    def __init__(self, base_prompt="") -> None:
        super().__init__(base_prompt)
        try:
            assert(os.environ["GIGA_AUTH"])
        except:
            raise BaseException("AUTH code is not provided")
        self._giga = GigaChat(credentials=os.environ["GIGA_AUTH"], verify_ssl_certs=False)
            

    def _base_call(self, payload: Chat):
        response = self._giga.chat(payload)
        response_content = response.choices[0].message.content
        return response_content


    def call(self, msg: str) -> str:
        payload = Chat(
                        messages=[
                            Messages(role=MessagesRole.SYSTEM, content = self._base_promt),
                            Messages(role=MessagesRole.USER, content=msg)],
                        temperature=0.001,
                        max_tokens=1000,
                        )
        return self._base_call(payload)
    

    def call_chat(self, messages: list[Messages]) -> str:
        payload = Chat(
            messages=messages,
            temperature=0.001,
            max_tokens=1000,
        )
        return self._base_call(payload)
    
    def extraction(self, query, docs):
        return "response"
        return super().extraction(query, docs)