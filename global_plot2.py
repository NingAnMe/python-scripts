#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/2
@Author  : AnNing
"""
import os

import numpy as np
from DV import dv_map
from PB.DRC import ReadMersiL1


import pickle


def main():

    pickle_file = 'fy3d_mersi_global.pickle'
    if not os.path.isfile(pickle_file):
        dir_path = "/home/gsics/nas03/CMA_GSICS/SourceData/FENGYUN-3D/MERSI/L1/ORBIT/2018/20180630"
        times = ['0800', '0805', '0810', '0815', '0820', '0825',
                 '0830', '0835', '0840', '0845', '0850', '0855',
                 '0900', '0905', '0910', '0915', '0920', '0925',
                 '0930', '0935', '0940', '0945', '0950', '0955',
                 '1000', '1005', '1010', '1015', '1020', '1025',
                 '1030', '1035', '1040', '1045', '1050', '1055',
                 '1100', '1110', '1115', '1120', '1125', '1130',
                 ]

        file_name = 'FY3D_MERSI_GBAL_L1_20180630_{}_1000M_MS.HDF'
        lon_all = list()
        lat_all = list()
        tbb_all = list()
        for i in times:
            in_file = os.path.join(dir_path, file_name.format(i))
            print in_file
            read_mersi_l1 = ReadMersiL1(in_file)

            lon = read_mersi_l1.get_longitude()
            lat = read_mersi_l1.get_latitude()
            tbb = read_mersi_l1.get_tbb()['CH_24']

            for d in [lat, lon, tbb]:
                index = np.isfinite(d)
                lat = lat[index]
                lon = lon[index]
                tbb = tbb[index]

            lon_all = np.append(lon_all, lon)
            lat_all = np.append(lat_all, lat)
            tbb_all = np.append(tbb_all, tbb)

            print(lon_all.shape, lat_all.shape, tbb_all.shape)

        data = {
            'lon': lon_all,
            'lat': lat_all,
            'tbb': tbb_all,
        }

        with open(pickle_file, 'wb') as f:
            pickle.dump(data, f)
    else:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)

    lat = data['lat']
    lon = data['lon']
    tbb = data['tbb']

    print(lat.shape, lon.shape, tbb.shape)

    out_file = 'FY3D+MERSI_TBB_GLOBAL_DISTRIBUTION.png'
    title = 'FY3D+MERSI TBB GLOBAL DISTRIBUTION CH_24 20180630'

    vmin = int(np.nanmin(tbb))
    vmax = int(np.nanmax(tbb))

    p = dv_map.dv_map()
    p.easyplot(lat, lon, tbb,  markersize=1, marker='s', vmin=vmin, vmax=vmax)
    p.title = title
    p.savefig(out_file)
    print '>>> {}'.format(out_file)


def plot_map_project(latitude, longitude,
                     count, out_file,
                     title=None, ptype=None,
                     vmin=None, vmax=None,
                     marker=None, markersize=None):
    if title is not None:
        title = title
    else:
        title = "Map"

    if vmin is not None:
        vmin = vmin

    if vmax is not None:
        vmax = vmax

    if marker is not None:
        marker = marker
    else:
        marker = 's'

    if markersize is not None:
        markersize = markersize
    else:
        markersize = 1

    p = dv_map.dv_map()

    p.easyplot(latitude, longitude, count, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker)
    p.title = title
    p.savefig(out_file)
    print '>>> {}'.format(out_file)


if __name__ == '__main__':
    main()
