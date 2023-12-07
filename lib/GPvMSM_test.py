import os
import requests
import numpy as np
import netCDF4 as nc
import winsound as ws
import logging

from datetime import datetime, timedelta
from tqdm import tqdm
from scipy.interpolate import griddata
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import BASE_URL, START_DATE, END_DATE, DOWNLOAD_FOLDER, INPUT_FILE, OUTPUT_FILE, PROCESS_YEAR, CORRECTION_VALUE, UPSCALING_METHOD

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GPvMSM_Downloder:
    def __init__(self, start_date, end_date, folder):
        self.start_date = start_date
        self.end_date = end_date
        self.folder = folder
        self.base_url = BASE_URL

    def download_files(self):
        existing_files = self._get_existing_files()
        dates_to_download = self._get_dates_in_range()
        missing_files = []

        for date in dates_to_download:
            if not self._is_file_downloaded(date, existing_files):
                missing_files.append(date.strftime("%Y%m%d"))

                self._download_file_for_date(date)

        if missing_files:
            logging.info(f"Missing files downloaded: {', '.join(missing_files)}")
        else:
            logging.info("No missing files")

    def _get_existing_files(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

            return []
        
        return set(os.listdir(self.folder))

    def _is_file_downloaded(self, date, existing_files):
        formatted_date = date.strftime("%m%d")
        filename = f"{date.year}{formatted_date}.nc"
        
        return filename in existing_files

            
    def _get_dates_in_range(self):
        delta = self.end_date - self.start_date
        
        return [self.start_date + timedelta(days=i) for i in range(delta.days + 1)]

    def _download_file_for_date(self, date):
        formatted_date = date.strftime("%m%d")
        url = f"{self.base_url}{date.year}/{formatted_date}.nc"
        local_filename = f"{date.year}{formatted_date}.nc"
        
        self._download_file(url, local_filename)

    def _download_file(self, url, local_filename):
        os.makedirs(self.folder, exist_ok=True)
        local_path = os.path.join(self.folder, local_filename)

        with requests.get(url, stream=True) as r:
            if r.status_code == 404:
                logging.error(f"Unable to download {local_filename}: 404 Client Error: Not Found for url: {url}")
                return

            logging.info(f"Downloading {local_filename}")

            with open(local_path, 'wb') as file:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            logging.info(f"Downloaded {local_filename}")


class DataProcessor:
    def __init__(self, year):
        self.year = year
        self.base_dir = f'./nc/GPvMSM/{year}/'
        self.output_dir = './nc/GPvMSM/yearly_data/'
        
        os.makedirs(self.output_dir, exist_ok=True)

    def process_year(self):
        days_in_year = 366 if DataProcessor._is_leap_year(self.year) else 365
        all_daily_rains = self._initialize_rain_data(days_in_year)

        first_file_path = os.path.join(self.base_dir, f'{self.year}0101.nc')
        
        with nc.Dataset(first_file_path, 'r') as data:
            lat = data.variables['lat'][:]
            lon = data.variables['lon'][:]

        for day in range(days_in_year):
            current_date = datetime(self.year, 1, 1) + timedelta(days=day)
            self._process_day(current_date, all_daily_rains, day)

        self._save_data(all_daily_rains, days_in_year, lat, lon)

    @staticmethod
    def _is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def _initialize_rain_data(self, days_in_year):
        first_file_path = os.path.join(self.base_dir, f'{self.year}0101.nc')
        
        with nc.Dataset(first_file_path, 'r') as data:
            lat_len, lon_len = len(data.variables['lat'][:]), len(data.variables['lon'][:])
            
        return np.zeros((days_in_year, lat_len, lon_len))

    def _process_day(self, current_date, all_daily_rains, day):
        file_path = os.path.join(self.base_dir, f'{current_date.strftime("%Y%m%d")}.nc')
        logging.info(f"Processing file: {file_path}")
        
        if os.path.isfile(file_path):
            
            with nc.Dataset(file_path, 'r') as data:
                daily_rain = np.sum(data.variables['r1h'][:], axis=0)
                all_daily_rains[day, :, :] = daily_rain

    def _save_data(self, all_daily_rains, days_in_year, lat, lon):
        output_file = os.path.join(self.output_dir, f'{self.year}.nc')
        
        with nc.Dataset(output_file, 'w', format='NETCDF4') as output_ds:
            output_ds.createDimension('time', None)
            output_ds.createDimension('lat', len(lat))
            output_ds.createDimension('lon', len(lon))

            time = output_ds.createVariable('time', np.int32, ('time',))
            latitudes = output_ds.createVariable('lat', np.float32, ('lat',))
            longitudes = output_ds.createVariable('lon', np.float32, ('lon',))
            rain = output_ds.createVariable('r1d', np.float32, ('time', 'lat', 'lon',))

            time[:] = np.arange(1, days_in_year + 1)
            latitudes[:] = lat
            longitudes[:] = lon

            rain[:, :, :] = all_daily_rains

            rain.units = 'mm/day'
            latitudes.units = 'degree_north'
            longitudes.units = 'degree_east'

class DataUpscaler:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def upscale_data(self):
        r1d, lat, lon, time = self._load_data()
        new_lat, new_lon = self._define_new_grid(lat, lon)
        upscaled_data = self._upscale_data(r1d, lat, lon, new_lat, new_lon)
        self._save_data(upscaled_data, new_lat, new_lon, time)

    def _load_data(self):
        with nc.Dataset(self.input_file) as dataset:
            r1d = dataset.variables['r1d'][:]
            lat = dataset.variables['lat'][:]
            lon = dataset.variables['lon'][:]
            time = dataset.variables['time'][:]
        return r1d, lat, lon, time

    def _define_new_grid(self, lat, lon):
        lat_interval = 0.50
        lon_interval = 0.50
        new_lat = np.arange(np.min(lat), np.max(lat), lat_interval)
        new_lon = np.arange(np.min(lon), np.max(lon), lon_interval)
        return new_lat, new_lon

####################################################################################################
############################ MAYBE HAV SOME PROBLEM IN THIS LOGIC###################################
####################################################################################################

    def _upscale_data(self, original_data, original_lat, original_lon, target_lat, target_lon):
        target_data = np.zeros((original_data.shape[0], len(target_lat), len(target_lon)))

        for t in range(original_data.shape[0]):
            for i, new_lat_val in enumerate(target_lat):
                for j, new_lon_val in enumerate(target_lon):
                    lat_lower = new_lat_val - 0.25
                    lat_upper = new_lat_val + 0.25
                    lon_lower = new_lon_val - 0.25
                    lon_upper = new_lon_val + 0.25

                    lat_in_cell = (original_lat >= lat_lower) & (original_lat < lat_upper)
                    lon_in_cell = (original_lon >= lon_lower) & (original_lon < lon_upper)

                    cell_data = original_data[t, lat_in_cell, :][:, lon_in_cell]

                    if cell_data.size > 0:
                        target_data[t, i, j] = np.nanmax(cell_data)
                        
                    else:
                        target_data[t, i, j] = np.nan

        return target_data

####################################################################################################

    def _save_data(self, data, lat, lon, time):
        with nc.Dataset(self.output_file, 'w', format='NETCDF4_CLASSIC') as dataset:
            dataset.createDimension('time', len(time))
            dataset.createDimension('lat', len(lat))
            dataset.createDimension('lon', len(lon))
            
            times = dataset.createVariable('time', 'f4', ('time',))
            latitudes = dataset.createVariable('lat', 'f4', ('lat',))
            longitudes = dataset.createVariable('lon', 'f4', ('lon',))
            r1d = dataset.createVariable('r1d', 'f4', ('time', 'lat', 'lon',))

            r1d.units = 'mm/day'
            times[:] = time
            latitudes[:] = lat
            longitudes[:] = lon
            r1d[:, :, :] = data
            

def main():
    start_date = datetime.strptime(START_DATE, "%Y/%m/%d")
    end_date = datetime.strptime(END_DATE, "%Y/%m/%d")
    
    downloader = GPvMSM_Downloder(start_date, end_date, DOWNLOAD_FOLDER) 
    downloader.download_files()  

    processor = DataProcessor(int(PROCESS_YEAR))
    processor.process_year()

    upscaler = DataUpscaler(INPUT_FILE, OUTPUT_FILE)
    upscaler.upscale_data()

    frequency = 2500  
    duration = 500  
    
    ws.Beep(frequency, duration)

if __name__ == "__main__":
    main()
