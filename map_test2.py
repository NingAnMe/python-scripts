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
    ARGS = sys.argv[1:]
    HELP_INFO = \
        u"""
        [arg1]：sat+sensor
        [arg2]：ymd-ymd
        [example]： python app.py arg1 arg2
        """
    if "-h" in ARGS:
        print HELP_INFO
        sys.exit(-1)

    if len(ARGS) != 2:
        print HELP_INFO
        sys.exit(-1)
    else:
        ARG1 = ARGS[0]
        ARG2 = ARGS[1]

    ymd_start, ymd_end = ARG2.split('-')

    in_path = '/GSICS/CMA_GSICS/SourceData/FENGYUN-3C/VIRR/L1/ORBIT/201501'
    out_path = 'Picture'

    pattern = r'.*(\d{8})_\d{4}_GEOXX'
    files = get_files_by_ymd(in_path, ymd_start, ymd_end, ext='.hdf', pattern_ymd=pattern)

    files = [
        '/nas03/GSICS/SourceData/FENGYUN-3A/VIRR/L1/ORBIT/200811/FY3A_VIRRX_GBAL_L1_20081106_2055_1000M_MS.HDF',
        '/nas03/GSICS/SourceData/FENGYUN-3A/VIRR/L1/ORBIT/200811/FY3A_VIRRX_GBAL_L1_20081106_2100_1000M_MS.HDF',
        '/nas03/GSICS/SourceData/FENGYUN-3A/VIRR/L1/ORBIT/200811/FY3A_VIRRX_GBAL_L1_20081106_2235_1000M_MS.HDF',
    ]

    for in_file in files:
        try:
            with h5py.File(in_file, 'r') as hdf5_file:
                if 'fy3c' in in_file.lower():
                    lats = hdf5_file.get('/Geolocation/Latitude')[:]
                    lons = hdf5_file.get('/Geolocation/Longitude')[:]
                else:
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

                pattern = r".*(\d{8})_(\d{4})"
                re_result = re.match(pattern, in_file)
                if re_result is not None:
                    ymd = re_result.groups()[0]
                    hm = re_result.groups()[1]
                    lonlatlocation = [(123.0, -74.5, u"Dome_C"), (23.39, 28.55, u"Libya4")]
                    p.add_landmark(lonlatlocation)
                    out_picture = '{}/{}_{}.png'.format(out_path, ymd, hm)
                    p.savefig(out_picture)
                    print '>>> {}'.format(out_picture)

        except Exception as why:
            print why
