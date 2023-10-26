from llm.wrappers.giga_wrapper import GigaWrapper
from dtaas_bot.llm.dbs.knowldge_base import KnowledgeBase
from langchain.llms import gigachat

from enum import Enum

class IntentType(Enum):
    UNDEFINED = 0
    CASES = 1

class Core():
    def __init__(self):
        self._llm = GigaWrapper()
        self._kb = KnowledgeBase()
        pass

    def process_message(self, message):
        """Обрабатывает сообщение пользователя"""

        #здесь определяю намерение пользователя
        user_intent = IntentType.CASES

        if user_intent == IntentType.CASES:
            self._process_dt_case_query(message)
        else:
            self._llm.call(message)


    def _process_dt_case_query(self, query):
        relevant_docs = self._kb.query(query)
        self._llm.extraction(query, docs=relevant_docs)
        

