
from chromadb.utils import embedding_functions
import logging
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os

class BaseManager():
    def __init__(self):
        pass

    def get_cases(self, msg, quantity = 1):
        retriever = self._base.as_retriever(search_kwargs={"k": quantity})
        results = retriever.get_relevant_documents(msg)
        return results
    
    def load_base(self, path="db"):
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
    
    def build_base(self, from_path="data", mode="prepared", persist_path="dbs/vector_db"):
        import pandas as pd
        metadata_columns = ['Отрасль','Заказчик', 'Исполнитель']
        main_info_columns = ['Заголовок', 'Текст кейса']

        df = pd.read_csv("data/dtaas_cases.csv", encoding="utf8", sep=";")


        def process_one_row(one_row, index):
            def clear_text(old_text):
                new_text = str(old_text).replace("\n\n\n", "\n").replace("\n\n", "\n")
                return new_text
            metadata = one_row[metadata_columns].to_dict()
            main_info_raw = one_row[main_info_columns]
            main_info = "\n".join([f"{k}:{clear_text(v)}" for k,v in main_info_raw.to_dict().items()])
            result = {"id":"id"+str(index), "metadata":metadata, "data":main_info}
            return result
        
        processed_cases = [process_one_row(row, i) for i, row in df.iterrows()]

        docs = list()
        meta = list()
        indexes = list()
        for c in processed_cases:
            docs.append(c["data"])
            meta.append(c["metadata"])
            indexes.append(c["id"])

        from langchain.vectorstores import Chroma
        from langchain.embeddings.openai import OpenAIEmbeddings

        vector_db = Chroma.from_texts(texts = docs, metadatas=meta, embedding=OpenAIEmbeddings(), persist_directory="db")
        return vector_db
    

