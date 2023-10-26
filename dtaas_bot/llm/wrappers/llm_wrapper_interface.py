
class Message():
    role: str
    content: str

class LLMWrapperInterface:
    def __init__(self, base_prompt = "") -> None:
        self._base_promt = base_prompt
        
    def call(self, msg: str) -> str:
        """Простой вызов LLM - одно сообщение на вход"""
        pass

    def call_chat(self, messages: list[Message]) -> str:
        """Вызов LLM с передачей истории и систем промптов"""
        pass

    def extraction(self, query:str, docs:list[str]) -> str:
        """Вызов LLM  с здачей извлечения ответа из передаваемых документов"""
        pass