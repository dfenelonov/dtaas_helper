import logging
import os
from preprocessor import DataPreprocessor

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


class VecBaseManager:
    def __init__(self, path_to_data, path_to_vectorized_db):
        logging.info("Initialising BaseManager for path")
        self._path_to_data = path_to_data
        self._path_to_vectorized_db = path_to_vectorized_db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def build_base(self):
        try:
            prep = DataPreprocessor(self._path_to_data)
            all_splits = prep.make_docs('excel')
            vectorstore = Chroma.from_texts(
                    texts=all_splits, embedding=OpenAIEmbeddings(), persist_directory=self._path_to_vectorized_db)
            vectorstore.persist()
            return vectorstore
        except Exception as e:
            pass

    def load_base(self):
        logging.info("Looking for persist vectorstore in " + self._path_to_vectorized_db)
        if os.path.exists(self._path_to_vectorized_db):
            logging.info("Path exist. Reading vectorstore from " + self._path_to_vectorized_db)
            vectordb = Chroma(persist_directory=self._path_to_vectorized_db,
                              embedding_function=OpenAIEmbeddings())
            return vectordb
        else:
            vectordb = self.build_base()
            return vectordb
