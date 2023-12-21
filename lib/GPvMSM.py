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

from config import (BASE_URL, START_DATE, END_DATE, DOWNLOAD_FOLDER, 
                    INPUT_FILE, OUTPUT_FILE, PROCESS_YEAR, 
                    CORRECTION_VALUE, DOWNSCALING_METHOD, 
                    LAT_GRID_SIZE, LON_GRID_SIZE, INPUT_FILE_SUM)

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
        local_path = os.path.join(self.folder, local_filename)

        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))

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

class DataProcessor:
    def __init__(self, year, download_folder, input_file):
        self.year = year
        self.base_dir = download_folder
        self.output_dir = os.path.dirname(input_file)
        
        os.makedirs(self.output_dir, exist_ok=True)

    def process_year(self):
        output_file_path = os.path.join(self.output_dir, f'{self.year}.nc')
        
        if os.path.isfile(output_file_path):
            logging.info(f"process skipped for {self.year} file already exists ")
            return

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

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

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

class getYearSum:
    def __init__(self, input_file):
        self.input_file = input_file
        self.nc_file = nc.Dataset(input_file, mode='r')
        self.lat = self.nc_file.variables['lat'][:]
        self.lon = self.nc_file.variables['lon'][:]
        self.time = self.nc_file.variables['time'][:]
        self.r1d = self.nc_file.variables['r1d'][:]
        self.reference_date = None

        input_file_name = os.path.basename(input_file)
        output_file_name = f"{input_file_name.split('.')[0]}_sum.nc"
        
        self.output_file = os.path.join(os.path.dirname(input_file), output_file_name)

        self.skip_processing = os.path.isfile(self.output_file)
        
        if self.skip_processing:
            logging.info(f"SUM : Output file already exists. Skipping processing.")
            
        else:
            logging.info(f"SUM : Processing {self.input_file} to create {self.output_file}")

    def aggregate_annual_data(self):
        if self.skip_processing:
            return None
        
        logging.info("SUM : Starting to aggregate annual data.")
        
        total_sum = np.zeros((len(self.lat), len(self.lon)))

        for time_idx in range(len(self.time)):
            current_day = int(self.time[time_idx])
            
            logging.info(f"Processing day: {current_day}")

            for lat_idx in range(len(self.lat)):
                for lon_idx in range(len(self.lon)):
                    total_sum[lat_idx, lon_idx] += self.r1d[time_idx, lat_idx, lon_idx]

        logging.info("SUM : Annual data aggregation completed.")
        return {'yearly_sum': total_sum}

    def convert_time_to_date(self):
        return [datetime(int(PROCESS_YEAR), 1, 1) + timedelta(days=int(day - 1)) for day in self.time]

    def get_max_value(self, annual_data):
            max_value = max([np.max(annual_data[year]) for year in annual_data])
            return max_value

    def save_to_new_file(self, annual_data):
        if self.skip_processing or annual_data is None:
            logging.info(f"SUM : Skipping saving sum process file already exists")
            return
        
        logging.info("SUM : Saving aggregated data to file: %s", self.output_file)

        with nc.Dataset(self.output_file, 'w', format='NETCDF4') as new_nc:
            new_nc.createDimension('lat', len(self.lat))
            new_nc.createDimension('lon', len(self.lon))
            new_nc.createDimension('time', 1)

            latitudes = new_nc.createVariable('lat', 'f4', ('lat',))
            longitudes = new_nc.createVariable('lon', 'f4', ('lon',))
            time = new_nc.createVariable('time', 'i4', ('time',))
            r1y = new_nc.createVariable('r1y', 'f4', ('time', 'lat', 'lon',))
            max_val_var = new_nc.createVariable('max_value', 'f4')

            max_val_var.units = 'mm/yr'
            max_val_var[:] = self.get_max_value(annual_data)

            latitudes[:] = self.lat
            longitudes[:] = self.lon
            time[:] = [int(PROCESS_YEAR)]
            r1y[0, :, :] = annual_data['yearly_sum']

            latitudes.units = 'degree_north'
            longitudes.units = 'degree_east'
            time.units = 'years'
            r1y.units = 'mm/yr'

            new_nc.description = "Annual aggregated precipitation data"
            
            logging.info("SUM : Data saved successfully to %s", self.output_file)

class DataDownscaler:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

        self.lat_grid_size = float(LAT_GRID_SIZE)
        self.lon_grid_size = float(LON_GRID_SIZE)

        self.downscaling_method = DOWNSCALING_METHOD
        
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        self._setup_logging()

    def downscale_data(self):
        try:
            r1y, lat, lon, time = self._load_data()
            new_lat, new_lon = self._define_new_grid(lat, lon)
            downscaled_data = self._downscale_data_method(r1y, lat, lon, new_lat, new_lon)
            self._save_data(downscaled_data, new_lat, new_lon, time)

            logging.info("Data downscaling completed successfully.")
            
        except Exception as e:
            logging.error(f"Error during data downscaling: {e}")

    def _load_data(self):
        if not os.path.exists(os.path.dirname(self.input_file)):
            os.makedirs(os.path.dirname(self.input_file))

        with nc.Dataset(self.input_file) as dataset:
            r1y = dataset.variables['r1y'][:]
            lat = dataset.variables['lat'][:]
            lon = dataset.variables['lon'][:]
            time = dataset.variables['time'][:]
            
        logging.info("Dataset opened successfully.")
        
        return r1y, lat, lon, time

    def _define_new_grid(self, lat, lon):
        new_lat = np.arange(np.min(lat), np.max(lat), self.lat_grid_size)
        new_lon = np.arange(np.min(lon), np.max(lon), self.lon_grid_size)
        
        return new_lat, new_lon

    def _downscale_data_method(self, original_data, original_lat, original_lon, target_lat, target_lon):
        target_data = np.zeros((len(target_lat), len(target_lon)))
        
        for i, new_lat_val in enumerate(target_lat):
            for j, new_lon_val in enumerate(target_lon):
                lat_lower_bound, lat_upper_bound = self._calculate_bounds(new_lat_val, self.lat_grid_size)
                lon_lower_bound, lon_upper_bound = self._calculate_bounds(new_lon_val, self.lon_grid_size)

                lat_in_cell = (original_lat >= lat_lower_bound) & (original_lat < lat_upper_bound)
                lon_in_cell = (original_lon >= lon_lower_bound) & (original_lon < lon_upper_bound)

                cell_data = original_data[:, lat_in_cell, :][:, :, lon_in_cell]
                
                if cell_data.size > 0:
                    target_data[i, j] = self._aggregate_data(cell_data)
                    
                else:
                    target_data[i, j] = np.nan

        return target_data

    def _calculate_bounds(self, center_val, grid_size):
        half_grid = grid_size / 2.0
        lower_bound = center_val - half_grid
        upper_bound = center_val + half_grid
        
        return lower_bound, upper_bound

    def _aggregate_data(self, cell_data):
        if self.downscaling_method == 'max':
            return np.nanmax(cell_data)
        
        elif self.downscaling_method == 'median':
            return np.nanmedian(cell_data)
        
        elif self.downscaling_method == 'center':
            return self._calculate_center_value(cell_data)
        
        else:  
            return np.nanmean(cell_data)

    def _calculate_center_value(self, cell_data):
        rows, cols = cell_data.shape

        center_row = rows // 2
        center_col = cols // 2

        if rows % 2 == 1 and cols % 2 == 1:
            return cell_data[center_row, center_col]
        
        else:
            center_values = cell_data[center_row-1:center_row+1, center_col-1:center_col+1]
            return np.nanmean(center_values)

    def get_max_value(self, downscaled_data):
        return np.nanmax(downscaled_data)

    def _save_data(self, data, lat, lon, time):
        with nc.Dataset(self.output_file, 'w', format='NETCDF4') as new_nc:
            new_nc.createDimension('lat', len(lat))
            new_nc.createDimension('lon', len(lon))
            new_nc.createDimension('time', len(time))

            latitudes = new_nc.createVariable('lat', 'f4', ('lat',))
            longitudes = new_nc.createVariable('lon', 'f4', ('lon',))
            times = new_nc.createVariable('time', 'i4', ('time',))
            r1y = new_nc.createVariable('r1y', 'f4', ('time', 'lat', 'lon',))
            max_val_var = new_nc.createVariable('max_value', 'f4')

            max_val_var.units = 'mm/yr'
            max_val_var[:] = self.get_max_value(data)

            latitudes[:] = lat
            longitudes[:] = lon
            times[:] = time
            r1y[:, :] = data

            latitudes.units = 'degree_north'
            longitudes.units = 'degree_east'
            times.units = 'years'
            
            r1y.standard_name ='precipitation_flux' 
            r1y.long_name = 'Precipitation'
            r1y.units = 'mm/yr'
            
            new_nc.description = "Downscaled GPVMSM annual precipitation data"
            logging.info("Data saved successfully to %s", self.output_file)

    def _setup_logging(self):
        logging.basicConfig(filename='downscaler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    start_date = datetime.strptime(START_DATE, "%Y/%m/%d")
    end_date = datetime.strptime(END_DATE, "%Y/%m/%d")
    
    downloader = GPvMSM_Downloder(start_date, end_date, DOWNLOAD_FOLDER) 
    downloader.download_files()  

    processor = DataProcessor(int(PROCESS_YEAR), DOWNLOAD_FOLDER, INPUT_FILE)
    processor.process_year()
    
    aggregator = getYearSum(INPUT_FILE)
    annual_sum = aggregator.aggregate_annual_data()
    aggregator.save_to_new_file(annual_sum) 

    downscaler = DataDownscaler(INPUT_FILE_SUM, OUTPUT_FILE)
    downscaler.downscale_data()

    frequency = 2500  
    duration = 500  
    
    ws.Beep(frequency, duration)

if __name__ == "__main__":
    main()
