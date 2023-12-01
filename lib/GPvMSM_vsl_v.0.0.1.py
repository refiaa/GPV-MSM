import matplotlib.pyplot as plt
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import os
from io import BytesIO
import imageio.v2 as imageio
import time
import winsound

from shapely.geometry import box
from datetime import datetime, timedelta
from PIL import Image


###########################################################################################
################################ WORK CONFIRMED 231128 ################# ver. 0.0.1 #######
###########################################################################################

##################################### DESCRIPTION #########################################
#                                                                                         #
#                                WRAPING LAT ISNT USED                                    #
#                                                                                         #
###########################################################################################

################################# netCDF FILE VARIABLE ####################################

nc_filename = '2015_upscaled_max.nc'
variable_name = 'r1d'

lon_min = 120
lon_max = 150
lat_min = 22.40
lat_max = 47.60

resolution = (1190, 1000, 800)  
max_value = 15

year = 2015

start_date = '08/01'
end_date = '08/31'

gif_filename = 'testing_v0.0.2.gif'

color_map = 'coolwarm' 
frame_duration = 125
transparency = 0.7

###########################################################################################

if not os.path.exists('./plot'):
    os.makedirs('./plot')

def wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max):
    
    lon_mask = (lon >= lon_min) & (lon <= lon_max)
    lat_mask = (lat >= lat_min) & (lat <= lat_max)

    data = data[:, lat_mask, :]
    data = data[:, :, lon_mask]

    return lon[lon_mask], lat[lat_mask][::-1], data

def crop_map(data, lon_min, lon_max, lat_min, lat_max):
    return data.cx[lon_min:lon_max, lat_min:lat_max]

def convert_to_date(time_val, year):
    return datetime(year, 1, 1) + timedelta(days=time_val - 1)

def create_GIF(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name):
    dataset = nc.Dataset(nc_file)
    
    lon = dataset.variables['lon'][:]
    lat = dataset.variables['lat'][:]
    
    time = dataset.variables['time'][:]

    def convert_to_date(day_of_year, year):
        return datetime(year, 1, 1) + timedelta(days=day_of_year - 1)

    dates = [convert_to_date(int(t), year) for t in time]

    user_start_date_dt = datetime.strptime(f'{year}/{start_date}', '%Y/%m/%d')
    user_end_date_dt = datetime.strptime(f'{year}/{end_date}', '%Y/%m/%d')

    data = dataset.variables[variable_name][:]

    lon, lat, data = wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max)

    frames = []

    fig, ax = plt.subplots(figsize=(resolution[0] / 100, resolution[1] / 100))
    world.boundary.plot(ax=ax, linewidth=1, color='k')

    im = ax.imshow(data[0, ::-1, :], extent=(lon_min, lon_max, lat_min, lat_max), cmap=color_map, alpha=transparency, vmax=max_value)
    colorbar = fig.colorbar(im, ax=ax, label=f'{variable_name} ({dataset.variables[variable_name].units})')
    title = ax.set_title('')

    for i in range(len(dates)):
        current_date = dates[i]

        if user_start_date_dt <= current_date <= user_end_date_dt:
            im.set_data(data[i, ::-1, :])
            title.set_text(f'Time: {current_date.strftime("%Y/%m/%d")}')

            with BytesIO() as buf:
                plt.savefig(buf, format='png', dpi=resolution[2], bbox_inches='tight')
                buf.seek(0)
                
                frame = Image.open(buf)
                frame = frame.resize(resolution[:2])
                frames.append(frame)

    if frames:
        frames[0].save(gif_file_path, save_all=True, append_images=frames[1:], duration=frame_duration, loop=0)
        
    else:
        print("No frames generated within the specified date range.")

    plt.close(fig)

    dataset.close()
    
try:
    world = gpd.read_file('./shp/World_Countries_Generalized.shp')

except Exception as e:
    print(f"Fail to load shapefile: {str(e)}")

BASE_NC_DIR = './nc/GPvMSM/yearly_data/'
BASE_GIF_DIR = './plot/'

nc_file = os.path.join(BASE_NC_DIR, nc_filename)
gif_file_path = os.path.join(BASE_GIF_DIR, gif_filename)

create_GIF(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name)

frequency = 2500  
duration = 500  

winsound.Beep(frequency, duration)

