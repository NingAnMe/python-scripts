#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/1/4
@Author  : AnNing
"""
import re
from datetime import datetime

import h5py
import numpy as np
from PB.pb_io import get_files_by_ymd

from lib_gsics.lib_gsics_plot_core import plot_timeseries


def main():
    # Greenland Dome_C AtlanticN PacificN1

    # [200, 250]  [220, 320]

    dir_path = '/nas03/CMA_GSICS_TEST/PICS/SupportData/PreprocessingData/FY3A+MERSI/3_L2/'
    pattern_ymd = r".*(\d{8})_.*PacificN1"
    in_files = get_files_by_ymd(dir_path, '20080101', '20181231', pattern_ymd=pattern_ymd)
    in_files.sort()
    data = []
    dates = []
    sets = set()
    for in_file in in_files:
        pattern = r".*(\d{8})"
        re_result = re.match(pattern, in_file)
        date_hdf5 = re_result.groups()[0]
        if date_hdf5 in sets:
            continue
        date_hdf5 = datetime.strptime(date_hdf5, '%Y%m%d')
        print date_hdf5

        try:
            with h5py.File(in_file, 'r') as hdf5:
                data_hdf5 = hdf5.get('CH_05/TBB_avg').value
                data.append(data_hdf5)
                dates.append(date_hdf5)
                sets.add(date_hdf5)
        except:
            continue

    fix_name = 'PacificN1'

    out_file = 'test/{}.png'.format(fix_name)

    title = '{} CH05 TBB Timeseries 20080101-20181231'.format(fix_name)

    y = np.array(data).reshape(-1)
    x = np.array(dates).reshape(-1)

    plot_timeseries(
        out_file=out_file,
        data_x=x,
        data_y=y,
        title=title,
        y_range=[220., 320.],
        y_interval=10,
        y_label='TBB (K)',
        ymd_start='20080101', ymd_end='20181231',
        plot_month=False,
        plot_zeroline=False)


if __name__ == '__main__':
    main()
