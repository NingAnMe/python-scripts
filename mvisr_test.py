#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/7/18 14:43
@Author  : AnNing
"""
import os
import sys
from PB.DRC.pb_drc_MVISR_L1 import CLASS_MVISR_L1
from PB.pb_time import time_block
from PB.pb_io import get_files_by_ymd
from DV.dv_map import dv_map


if __name__ == '__main__':
    in_path = r'E:\projects\six_sv_data'
    # in_files = get_files_by_ymd(in_path, '200205181821', '200205181821', '.hdf', r".*FY1D.*GDPT_(\d{8})_(\d{4})")
    in_files = [os.path.join(in_path, 'FY1D_L1_GDPT_20020519_0800.HDF')]
    for in_file in in_files:
        with time_block('all'):
            mvisr = CLASS_MVISR_L1()
            mvisr.Load(in_file)
            print mvisr.ir_coeff_k0['CH_01'].shape
            print mvisr.ir_coeff_k1['CH_01'].shape
            print mvisr.Time.shape
            print mvisr.Lats.shape
            print mvisr.Lons.shape
        lat_0 = 28.550000
        lon_0 = 23.390000
        lat_max = lat_0 + 3
        lat_min = lat_0 - 3
        lon_max = lon_0 + 3
        lon_min = lon_0 - 3

        picture_name = os.path.basename(in_file).split('.')[0] + '.png'
        out_picture = os.path.join('picture', picture_name)

        box = [lat_max, lat_min, lon_min, lon_max]
        # box = [60, 10, 70, 150]
        p = dv_map()

        print len(mvisr.Lats)
        with time_block('plot'):
            print mvisr.Lats
            print mvisr.Lons
            print mvisr.Dn['CH_01']
            p.easyplot(mvisr.Lats, mvisr.Lons, mvisr.Dn['CH_01'], vmin=None, vmax=None,
                       ptype=None, markersize=0.1, marker='o')

        lonlatlocation = [(123.0, -74.5, u"Dome_C"), (23.39, 28.55, u"Libya4")]
        p.add_landmark(lonlatlocation)
        p.savefig(out_picture)
        print out_picture
