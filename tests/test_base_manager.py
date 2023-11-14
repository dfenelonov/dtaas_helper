from dotenv import load_dotenv
import sys
import os
from dtaas_bot.main import DtaasHelper
from dtaas_bot.vec_base_manager import VecBaseManager


def test_build_base():
    bot = DtaasHelper()
    bot.run()


def test_build_vs():
    with VecBaseManager('../dtaas_bot/data/Кейсы ЦТ - 2.xlsx', '/chroma_db') as vbm:
        vs = vbm.load_base()
    assert(vs)