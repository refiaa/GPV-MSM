import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

PROCESS_YEAR = os.environ.get('PROCESS_YEAR', '2015')  
DOWNSCALING_METHOD = os.environ.get('DOWNSCALING_METHOD', 'max')

BASE_URL = os.environ.get('BASE_URL', 'http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/netcdf/MSM-S/r1h/')

START_DATE = f"{PROCESS_YEAR}/01/01"
END_DATE = f"{PROCESS_YEAR}/12/31"
DOWNLOAD_FOLDER = f'./nc/GPvMSM/{PROCESS_YEAR}'
INPUT_FILE = f'./nc/GPvMSM_year/{PROCESS_YEAR}.nc'
INPUT_FILE_SUM = f'./nc/GPvMSM_year/{PROCESS_YEAR}_sum.nc'
OUTPUT_FILE = f'./nc/GPvMSM_DownScaled/{PROCESS_YEAR}_{DOWNSCALING_METHOD}.nc'

LAT_GRID_SIZE = float(os.environ.get('LAT_GRID_SIZE', 0.50))
LON_GRID_SIZE = float(os.environ.get('LON_GRID_SIZE', 0.50))