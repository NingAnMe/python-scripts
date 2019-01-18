#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/1/18
@Author  : AnNing
在 42 上面跑 FY1D L1 的转换
"""
import os

EXE = r'D:\extr_fy1_1b\Debug\extr_fy1_1b.exe'

IN_DIRS = [r'V:/FY1CD/NEW_FY1D/FY1D/GDPT',
           r'V:/FY1CD/NEW_FY1D/FY1D/HRPT']

OUT_DIR_GDPT = r'V:/FY1CD/FY1D-GDPT/FY1D_GDPT_L1_HDF'
OUT_DIR_HRPT = r'V:/FY1CD/FY1D_HRPT_HDF/FY1D_HRPT_HDF'


def main():
    # FY1D_AVHRR_GDPT_L1_ORB_MLT_NUL_20060119_2008_4000M_PJ.1A5
    # FY1D_AVHRR_HRPT_L1_ORB_MLT_NUL_20080101_0100_1100M_PJ.L1B
    for in_dir in IN_DIRS:  # 循环 GDPT 和 HRPT
        for year in ['2008', '2009', '2010', '2011', '2012']:  # 循环 GDPT 和 HRPT
            in_dir_year = os.path.join(in_dir, year)
            filenames = os.listdir(in_dir_year)
            filenames.sort()

            for filename in filenames:
                in_file = os.path.join(in_dir_year, filename)

                if 'GDPT' in filename:
                    out_dir = OUT_DIR_GDPT
                else:
                    out_dir = OUT_DIR_HRPT

                sat = filename.split('_')[0]
                ymd = filename.split('_')[7]
                hms = filename.split('_')[8]
                filename = '{}_L1_{}_{}.HDF'.format(sat, ymd, hms)
                out_file = os.path.join(out_dir, year, filename)

                cmd = '{} {} {}'.format(EXE, in_file, out_file)
                os.system(cmd)


if __name__ == '__main__':
    main()
