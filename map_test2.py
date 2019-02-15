#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/7/31 15:33
@Author  : AnNing
"""
import re
import os
import sys
import h5py
from DV.dv_map import dv_map
from PB.pb_io import get_files_by_ymd


if __name__ == '__main__':
    fy4_lon_lat_lut = 'FY4X_LON_LAT_LUT.H5'

    with h5py.File(fy4_lon_lat_lut, 'r') as hdf5_file:
        lats = hdf5_file.get('/Latitude')[:]
        lons = hdf5_file.get('/Longitude')[:]

        lat_0 = 28.550000
        lon_0 = 23.390000
        lat_max = lat_0 + 3
        lat_min = lat_0 - 3
        lon_max = lon_0 + 3
        lon_min = lon_0 - 3

        box = [lat_max, lat_min, lon_min, lon_max]
        # box = [60, 10, 70, 150]
        p = dv_map()
        p.easyplot(lats, lons, lats, vmin=None, vmax=None,
                   ptype=None, markersize=0.1, marker='o', box=None)

        lonlatlocation = [(123.0, -74.5, u"Dome_C"), (23.39, 28.55, u"Libya4")]
        p.add_landmark(lonlatlocation)
        out_picture = 'map_test.png'
        p.savefig(out_picture)
        print '>>> {}'.format(out_picture)

