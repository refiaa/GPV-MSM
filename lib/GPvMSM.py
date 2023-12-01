import os
import requests
import numpy as np
import netCDF4 as nc
import winsound as ws

from datetime import datetime, timedelta
from tqdm import tqdm
from scipy.interpolate import griddata
from concurrent.futures import ThreadPoolExecutor, as_completed


class GPvMSM_Downloder:
    def __init__(self, start_date, end_date, folder):
        self.start_date = start_date
        self.end_date = end_date
        self.folder = folder
        self.base_url = "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/netcdf/MSM-S/r1h/"

    def download_files(self):
        for date in self._get_dates_in_range():
            self._download_file_for_date(date)

    # def download_files(self):
    #     dates = self._get_dates_in_range()
    #     with ThreadPoolExecutor(max_workers=5) as executor:
    #         futures = [executor.submit(self._download_file_for_date, date) for date in dates]
    #         for future in as_completed(futures):
    #             try:
    #                 future.result()
    #             except Exception as exc:
    #                 print(f'download Exception: {exc}')

    # wanna use it in futher change in better way 

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
                print(f"Unable to download {local_filename}: 404 Client Error: Not Found for url: {url}")
                return

            total = int(r.headers.get('content-length', 0))
            
            with open(local_path, 'wb') as file, tqdm(
                    desc=local_filename,
                    total=total,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                
                for chunk in r.iter_content(chunk_size=1024):
                    bar.update(file.write(chunk))

            print(f"Downloaded {local_filename}")

class dataProcessor:
    def __init__(self, year):
        self.year = year
        self.base_dir = f'./nc/GPvMSM/{year}/'
        self.output_dir = './nc/GPvMSM/yearly_data/'
        
        os.makedirs(self.output_dir, exist_ok=True)

    def process_year(self):
        days_in_year = 366 if self._is_leap_year(self.year) else 365
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
    def _is_leap_year(self, year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def _initialize_rain_data(self, days_in_year):
        first_file_path = os.path.join(self.base_dir, f'{self.year}0101.nc')
        
        with nc.Dataset(first_file_path, 'r') as data:
            lat_len, lon_len = len(data.variables['lat'][:]), len(data.variables['lon'][:])
            
        return np.zeros((days_in_year, lat_len, lon_len))

    def _process_day(self, current_date, all_daily_rains, day):
        file_path = os.path.join(self.base_dir, f'{current_date.strftime("%Y%m%d")}.nc')
        
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

class dataUpscaler:
    def __init__(self, input_file, output_file, method='max'):
        self.input_file = input_file
        self.output_file = output_file
        self.method = method

    def upscale_data(self):
        r1d, lat, lon, time = self._load_data()
        new_lat, new_lon = self._define_new_grid(lat, lon)
        upscaled_data = self._aggregate_data(r1d, lat, lon, new_lat, new_lon)
        
        self._save_data(upscaled_data, new_lat, new_lon, time)

    def _load_data(self):
        dataset = nc.Dataset(self.input_file)
        r1d = dataset.variables['r1d'][:]
        lat = dataset.variables['lat'][:]
        lon = dataset.variables['lon'][:]
        time = dataset.variables['time'][:]
        
        return r1d, lat, lon, time

    def _define_new_grid(self, lat, lon):
        new_lat = np.arange(min(lat), max(lat), 0.5)
        new_lon = np.arange(min(lon), max(lon), 0.5)
        
        return new_lat, new_lon

    def _aggregate_data(self, original_data, original_lat, original_lon, target_lat, target_lon):
        target_data = np.zeros((original_data.shape[0], len(target_lat), len(target_lon)))
        for t in range(original_data.shape[0]):
            
            for i, lat in enumerate(target_lat):
                
                for j, lon in enumerate(target_lon):
                    
                    lat_mask = (original_lat >= lat - 0.25) & (original_lat < lat + 0.25)
                    lon_mask = (original_lon >= lon - 0.25) & (original_lon < lon + 0.25)
                    data_subset = original_data[t, lat_mask, :][:, lon_mask]
                    
                    if self.method == 'max':
                        target_data[t, i, j] = np.nanmax(data_subset)
                        
                    elif self.method == 'median':
                        target_data[t, i, j] = np.nanmedian(data_subset)
                        
                    else:
                        target_data[t, i, j] = np.nanmean(data_subset)
                        
        return target_data

    def _save_data(self, data, lat, lon, time):
        dataset = nc.Dataset(self.output_file, 'w', format='NETCDF4_CLASSIC')
        
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

        dataset.close()

def main():
    start_date_str = '2015/01/01'
    end_date_str = '2015/12/31'
    download_folder = "./nc/GPvMSM/2015"
    
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
    end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
    
    downloader = GPvMSM_Downloder(start_date, end_date, download_folder) 
    downloader.download_files()  

    processor = dataProcessor(2015)
    processor.process_year()

    upscaler = dataUpscaler('./nc/GPvMSM/yearly_data/2015.nc', './nc/GPvMSM/yearly_data/2015_upscaled.nc')
    upscaler.upscale_data()

    frequency = 2500  
    duration = 500  
    
    ws.Beep(frequency, duration)

if __name__ == "__main__":
    main()
