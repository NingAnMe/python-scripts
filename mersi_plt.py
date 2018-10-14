# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 15:50:55 2018

@author: timhung
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import h5py
from mpl_toolkits.basemap import Basemap


def Get_File(filedir):
    filename_arr = []
    time_arr = []
    for filename in os.listdir(filedir):
        if os.path.splitext(filename)[1] == '.HDF':
            filename_arr = np.concatenate((filename_arr, \
                                           [filename]))
            time = filename[-17:-13]
            time_arr = np.concatenate((time_arr, [time]))
            
    return filename_arr, time_arr

def Get_Data(file_path, data_set):
    h5 = h5py.File(file_path)
    data_arr = np.asarray(h5[data_set][:])
    h5.close()
    return data_arr

def Value_Data(data):
    return np.max(data), np.min(data)

mersi_geo_url = 'C:\\CrIS_HIRAS_MATCH\\HIRAS\\MERSI\\L1\\GEO1K\\'
mersi_1km_url = 'C:\\CrIS_HIRAS_MATCH\\HIRAS\\MERSI\\L1\\1000M\\'

geo_lon = 'Geolocation/Longitude'
geo_lat = 'Geolocation/Latitude'
rad_1km = 'Data/EV_250_Aggr.1KM_Emissive'

mersi_geo, mersi_geo_time = Get_File(mersi_geo_url+'20180420\\')
mersi_1km, mersi_1km_time = Get_File(mersi_1km_url+'20180420\\')

mersi_geo_lon = Get_Data(os.path.join(mersi_geo_url,'20180420\\',
                                     mersi_geo[0]),
                geo_lon)
mersi_geo_lat = Get_Data(os.path.join(mersi_geo_url,'20180420\\',
                                     mersi_geo[0]),
                geo_lat)
mersi_rad_1km = Get_Data(os.path.join(mersi_1km_url,'20180420\\',
                                      mersi_1km[0]),
                rad_1km)
mersi_rad_ch24 = mersi_rad_1km[0,:,:] * 0.01

height = 5
width = 4
fig = plt.figure(figsize=(height, width))  # 储存为一张可调整大小的图片
ax = plt.subplot2grid((1, 1), (0, 0))  # 使用子图

m = Basemap(projection='cyl', resolution='c',
            llcrnrlon=-180, llcrnrlat=-90,
            urcrnrlon=180, urcrnrlat=90,
            ax=ax)  # 使用ax参数

# with time_block('plot'):
#     mp = m.pcolor(mersi_geo_lon, mersi_geo_lat, mersi_rad_ch24,
#                   latlon=True, cmap='rainbow')


# 使用 BaseMap 自己的经纬度转换
x, y = m(mersi_geo_lon, mersi_geo_lat)
ms = m.scatter(x, y, marker='s', s=0.01, c=mersi_rad_ch24, cmap='rainbow', lw=0)
# with time_block('plot scatter'):
#     ms = m.scatter(np.squeeze(mersi_geo_lon), np.squeeze(mersi_geo_lat),
#              latlon=True,
#              c=np.squeeze(mersi_rad_ch24), cmap='rainbow')
cbar = m.colorbar(ms, location='bottom', pad='15%')

#m.imshow(mersi_rad_ch24, cmap='rainbow')

#cs = m.pcolor(mersi_geo_lon, mersi_geo_lat,
#              np.squeeze(mersi_rad_ch24))

interval = 30.
m.drawcoastlines()
#m.fillcontinents()
m.drawparallels(np.arange(-90.,91.,interval),
               labels=[True,False,False,False])
m.drawmeridians(np.arange(-180.,180.,interval),
                labels=[False,False,False,True])

# 清晰度
dpi = 200
fig.savefig('test.png', dpi=dpi)
