from dotenv import load_dotenv
import sys
import os
from dtaas_bot.db import DB_Handler
sys.path.insert(0, os.path.abspath("../TG_BOT_LLM"))

def test_build_base():
    db = DB_Handler()
    assert(db)