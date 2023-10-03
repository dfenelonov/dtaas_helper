from dotenv import load_dotenv
import logging
from dtaas_bot.base_manager import BaseManager
import sys
import os
sys.path.insert(0, os.path.abspath("../TG_BOT_LLM"))

def test_build_base():
    bm = BaseManager()
    vs = bm.build_base()
    assert(vs)

def test_load_base():
    bm = BaseManager()
    vs = bm.load_base()
    assert(vs)