import os
import netCDF4 as nc
import matplotlib.pyplot as plt
import geopandas as gpd
import winsound as ws
import numpy as np

from PIL import Image, ImageDraw 
from io import BytesIO

class NCDataProcessor:
    def __init__(self, DIRECTORY_PATH, SHAPEFILE_PATH, OUTPUT_PATH, LON_RANGE, LAT_RANGE, RESOLUTION, TRANSPARENCY, MAX_VALUE, color_map, FRAME_DURATION):
        self.DIRECTORY_PATH = DIRECTORY_PATH
        self.SHAPEFILE_PATH = SHAPEFILE_PATH
        self.OUTPUT_PATH = OUTPUT_PATH
        self.LON_RANGE = LON_RANGE
        self.LAT_RANGE = LAT_RANGE
        self.RESOLUTION = RESOLUTION
        self.TRANSPARENCY = TRANSPARENCY
        self.MAX_VALUE = MAX_VALUE
        self.color_map = color_map
        self.FRAME_DURATION = FRAME_DURATION

        if not os.path.exists(self.OUTPUT_PATH):
            os.makedirs(self.OUTPUT_PATH)

        try:
            self.world = gpd.read_file(self.SHAPEFILE_PATH)
            
        except Exception as e:
            print(f"Failed to load shapefile: {str(e)}")
            self.world = None

    def process_files(self, start_year, end_year):
        for file_name in self.scan_directory():
            nc_file = os.path.join(self.DIRECTORY_PATH, file_name)
            gif_filename = self.generate_output_filename(file_name)
            gif_file_path = os.path.join(self.OUTPUT_PATH, gif_filename)

            print(f"Processing file: {file_name}")  
            
            self.create_gif(nc_file, gif_file_path, start_year, end_year)
            self.verify_coordinates(nc_file)
        
        ws.Beep(frequency, duration)

    def scan_directory(self):
        return [file for file in os.listdir(self.DIRECTORY_PATH) if file.endswith('.nc')]

    def generate_output_filename(self, input_filename):
        base_filename = input_filename.rsplit('.', 1)[0]
        
        return f"{base_filename}.gif"
    
    def create_gif(self, nc_file, gif_file_path, start_year, end_year):
        with nc.Dataset(nc_file) as dataset:
            variable_name = list(dataset.variables.keys())[3]
            lon = dataset.variables['lon'][:]
            lat = dataset.variables['lat'][:]
            data = dataset.variables[variable_name][:]

            max_value = None
            
            if 'max_value' in dataset.variables:
                max_value = dataset.variables['max_value'][:]
            
            for year in range(start_year, end_year + 1):
                self.process_year_data(nc_file, data, lon, lat, year, gif_file_path, max_value, self.DIRECTORY_PATH)

    def process_year_data(self, nc_file, data, lon, lat, year, gif_file_path, max_value=None, directory_path=None):
        year_data = data[0]

        fig, ax = plt.subplots(figsize=(self.RESOLUTION[0] / 100, self.RESOLUTION[1] / 100))
        
        if self.world is not None:
            self.world.boundary.plot(ax=ax, linewidth=1, color='k')

        im = ax.imshow(year_data[::-1, :], extent=(self.LON_RANGE[0], self.LON_RANGE[1], self.LAT_RANGE[0], self.LAT_RANGE[1]), cmap=self.color_map, alpha=self.TRANSPARENCY, vmax=self.MAX_VALUE)

        with nc.Dataset(nc_file) as dataset:
            variable_name = list(dataset.variables.keys())[3]
            variable_units = dataset.variables[variable_name].units

            time_var = dataset.variables['time']
            year = int(time_var[0])

        colorbar = fig.colorbar(im, ax=ax, label=f'{variable_name} ({variable_units})')
        
        title_text = f'Year: {year}'
        title_text += f', Max Value: {max_value}'

        ax.set_title(title_text)

        with BytesIO() as buf:
            plt.savefig(buf, format='png', dpi=self.RESOLUTION[2], bbox_inches='tight')
            buf.seek(0)
            frame = Image.open(buf)
            frame = frame.resize(self.RESOLUTION[:2])
            frame.save(gif_file_path, format='GIF')

        plt.close(fig)
        
    def verify_coordinates(self, nc_file):
        with nc.Dataset(nc_file) as dataset:
            lon = dataset.variables['lon'][:]
            lat = dataset.variables['lat'][:]

        lon_grid, lat_grid = np.meshgrid(lon, lat)

        fig, ax = plt.subplots()
        
        self.world.plot(ax=ax, color='white', edgecolor='black')
        
        ax.scatter(lon_grid, lat_grid, s=10, c='red', marker='o') 
        
if __name__ == "__main__":
    
    processor = NCDataProcessor(
        DIRECTORY_PATH='./nc/GPvMSM_DownScaled/',
        SHAPEFILE_PATH='./shp/World_Countries_Generalized.shp',
        OUTPUT_PATH='./plot',
        
        LON_RANGE=(120, 150),
        LAT_RANGE=(22.40, 47.60),
        
        RESOLUTION=(1190, 1000, 800),
        TRANSPARENCY=0.7,
        
        MAX_VALUE=5000,
        
        color_map='coolwarm',
        FRAME_DURATION=125
    )
    
    frequency = 2500  
    duration = 500  

    ws.Beep(frequency, duration)

    START_YEAR = 2015
    END_YEAR = 2015
    
    processor.process_files(START_YEAR, END_YEAR)