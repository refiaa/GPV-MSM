import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

BASE_URL = os.environ.get('BASE_URL')
START_DATE = os.environ.get('START_DATE')
END_DATE = os.environ.get('END_DATE')
DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_FOLDER')
INPUT_FILE = os.environ.get('INPUT_FILE')
OUTPUT_FILE = os.environ.get('OUTPUT_FILE')
PROCESS_YEAR = os.environ.get('PROCESS_YEAR', 2015)  

CORRECTION_VALUE = float(os.environ.get('CORRECTION_VALUE'))