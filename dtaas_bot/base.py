import pandas as pd
import os
import dotenv
import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from base_manager import BaseManager

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

logging.debug("Читаем настройки среды")
dotenv.load_dotenv()
#os.environ["OPENAI_API_KEY"] = None
assert(os.environ["OPENAI_API_KEY"])
     

bm = BaseManager()
vs = bm.build_base()

#print(len(collection))



#print(df.shape)