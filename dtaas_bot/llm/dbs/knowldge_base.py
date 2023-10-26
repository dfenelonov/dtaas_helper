import logging
import os


class KnowledgeBase():
    def __init__(self, path):
        self._db = 
        pass

    def query(self, docs_num = 3):
        """
        Извлекает документы релевантные запросу
        param: docs_num - Коли
        """
        ##ToDo - извлечение из векторизованного хранилища похожих на запрос документов

        pass

    def _load_chroma_base(self, path="db"):
        logging.info("Looking for persist vectorstore in " + path)
        if os.path.exists(path):
            logging.info("Path exist. Reading vectorstore from " + path)
            vectordb = Chroma(persist_directory=path,
                              embedding_function=OpenAIEmbeddings())
            self._base = vectordb
            return vectordb
        else:
            logging.error("Path not found")
            return None