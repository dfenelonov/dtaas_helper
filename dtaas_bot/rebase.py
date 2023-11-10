import argparse
import logging
import configparser

from dotenv import load_dotenv
from vec_base_manager import VecBaseManager
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="folder where raw data is stored")
parser.add_argument("--to", help="folder where vector db will be stored")
args = parser.parse_args()
config = configparser.ConfigParser()

config.read('conf/config.conf')
path_to_data = config['DEFAULT']['path_to_data']
path_to_vectorized_db = config['DEFAULT']['path_to_vectorized_db']

source_folder = path_to_data if not args.source else args.source
destination_folder = path_to_vectorized_db if not args.to else args.to
print("Read from ", source_folder, "save to", destination_folder)

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

with VecBaseManager(source_folder, destination_folder) as vbm:
    vbm.build_base()
