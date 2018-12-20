#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/12/7
@Author  : AnNing
"""
import os
import numpy as np


class ReadOrbitCrossFile(object):
    """
    data:
        #### info #### 格式都是字符串
        sat1:  # 都有
        sat2:  # GEO_LEO和LEO_LEO是卫星名，LEO_AREA是区域名，LEO_FIX是“FIX”
        ymd： # ymd 交叉日期
        calc_time：  # 生成轨道预报的时间
        distance_max: # 距离固定点的最大距离  LEO_FIX 和LEO_LEO有
        solar_zenith_max:  # 太阳天顶角最大角度 LEO_FIX有
        # 区域范围： 只有区域和GEO_LEO有
        lat_n:
        lat_s:
        lon_w:
        lon_e:
        # 星下点
        geo_lat:
        geo_lon:

        #### data #### 格式都是列表
        # 如果只有s1，s2使用s1的数据，如果只有start，end和start相同。。
        hms_s_s1
        lat_s_s1
        lon_s_s1
        hms_e_s1
        lat_e_s1
        lon_e_s1

        hms_s_s2
        lat_s_s2
        lon_s_s2
        hms_e_s2
        lat_e_s2
        lon_e_s2

        # 特例，有返回，没有返回None
        fix_point  # 固定点名 LEO_FIX有
        distance
        second_diff
    """
    @staticmethod
    def read_cross_file(in_file, file_type):
        """
        :param in_file:
        :param file_type:
        :return:
        """
        data = {
            # 信息
            'sat1': None,
            'sat2': None,
            'ymd': None,
            'cal_time': None,
            'distance_max': None,
            'solar_zenith_max': None,
            'lat_n': None,
            'lat_s': None,
            'lon_w': None,
            'lon_e': None,
            'geo_lat': None,
            'geo_lon': None,
            # 数据
            'hms_s_s1': None,
            'lat_s_s1': None,
            'lon_s_s1': None,
            'hms_e_s1': None,
            'lat_e_s1': None,
            'lon_e_s1': None,
            'hms_s_s2': None,
            'lat_s_s2': None,
            'lon_s_s2': None,
            'hms_e_s2': None,
            'lat_e_s2': None,
            'lon_e_s2': None,
            'distance': None,
            'second_diff': None,
            'fix_point': None,
        }

        if not os.path.isfile(in_file):
            print '***WARNING***File is not exist: {}'.format(in_file)
            return data
        with open(in_file, 'r') as fp:
            lines_10 = fp.readlines()[0: 10]

            # count = 0
            # for line in lines_10:
            #     print count, line.split()
            #     count += 1

        if file_type == 'leo_area':
            # 信息
            data['sat1'] = lines_10[0].split()[1]
            data['sat2'] = lines_10[1].split()[1]
            data['ymd'] = lines_10[2].split()[1].replace('.', '')
            data['cal_time'] = lines_10[6].split()[3].replace('.', '') + lines_10[6].split()[
                4].replace(':', '')
            data['lat_n'] = lines_10[4].split()[2]
            data['lat_s'] = lines_10[4].split()[5]
            data['lon_w'] = lines_10[5].split()[2]
            data['lon_e'] = lines_10[5].split()[5]

            data_raw = np.loadtxt(in_file, skiprows=10, dtype={
                'names': ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7'),
                'formats': ('S8', 'S8', 'S8', 'f4', 'f4', 'f4', 'f4')})

            if data_raw.size != 0:

                data['hms_s_s1'] = data_raw['d2']
                data['lat_s_s1'] = data_raw['d4']
                data['lon_s_s1'] = data_raw['d5']
                data['hms_e_s1'] = data_raw['d3']
                data['lat_e_s1'] = data_raw['d6']
                data['lon_e_s1'] = data_raw['d7']

                data['hms_s_s2'] = data['hms_s_s1']
                data['lat_s_s2'] = data['lat_s_s1']
                data['lon_s_s2'] = data['lon_s_s1']
                data['hms_e_s2'] = data['hms_e_s1']
                data['lat_e_s2'] = data['lat_e_s1']
                data['lon_e_s2'] = data['lon_e_s1']

        elif file_type == 'leo_leo':
            # 信息
            data['sat1'] = lines_10[0].split()[1]
            data['sat2'] = lines_10[1].split()[1]
            data['ymd'] = lines_10[2].split()[1].split('-')[1]
            data['cal_time'] = lines_10[6].split()[3].replace('.', '') + lines_10[6].split()[
                4].replace(':', '')
            data['dist_max'] = lines_10[5].split()[3]

            data_raw = np.loadtxt(in_file, skiprows=10, dtype={
                'names': ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9'),
                'formats': ('S8', 'S8', 'f4', 'f4', 'S8', 'f4', 'f4', 'f4', 'f4')})

            if data_raw.size != 0:
                data['hms_s_s1'] = data_raw['d2']
                data['lat_s_s1'] = data_raw['d3']
                data['lon_s_s1'] = data_raw['d4']
                data['hms_e_s1'] = data['hms_s_s1']
                data['lat_e_s1'] = data['lat_s_s1']
                data['lon_e_s1'] = data['lon_s_s1']

                data['hms_s_s2'] = data_raw['d5']
                data['lat_s_s2'] = data_raw['d6']
                data['lon_s_s2'] = data_raw['d7']
                data['hms_e_s2'] = data['hms_s_s2']
                data['lat_e_s2'] = data['lat_s_s2']
                data['lon_e_s2'] = data['lon_s_s2']

                data['distance'] = data_raw['d8']
                data['second_diff'] = data_raw['d9']

        elif file_type == 'leo_fix':
            # 信息
            data['sat1'] = lines_10[0].split()[1]
            data['sat2'] = 'FIX'
            data['ymd'] = lines_10[1].split()[1].split('-')[1]
            data['cal_time'] = lines_10[6].split()[3].replace('.', '') + lines_10[6].split()[
                4].replace(':', '')
            data['dist_max'] = lines_10[2].split()[3]
            data['solar_zenith_max'] = lines_10[3].split()[4].strip('\xc2\xb0')

            # 数据
            data_raw = np.loadtxt(in_file, skiprows=10, dtype={
                'names': ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',),
                'formats': ('S8', 'S8', 'S8', 'f4', 'f4', 'f4', 'f4', 'f4')})

            if data_raw.size != 0:
                data['hms_s_s1'] = data_raw['d2']
                data['lat_s_s1'] = data_raw['d6']
                data['lon_s_s1'] = data_raw['d7']
                data['hms_e_s1'] = data['hms_s_s1']
                data['lat_e_s1'] = data['lat_s_s1']
                data['lon_e_s1'] = data['lon_s_s1']

                data['hms_s_s2'] = data['hms_s_s1']
                data['lat_s_s2'] = data_raw['d4']
                data['lon_s_s2'] = data_raw['d5']
                data['hms_e_s2'] = data['hms_s_s2']
                data['lat_e_s2'] = data['lat_s_s2']
                data['lon_e_s2'] = data['lon_s_s2']

                data['distance'] = data_raw['d8']
                data['fix_point'] = data_raw['d3']

        elif file_type == 'geo_leo':
            # 信息
            data['sat1'] = lines_10[0].split()[1]
            data['sat2'] = lines_10[1].split()[1]
            data['ymd'] = lines_10[2].split()[1].replace('.', '')
            data['cal_time'] = lines_10[6].split()[3].replace('.', '') + lines_10[6].split()[
                4].replace(':', '')
            data['lat_n'] = lines_10[4].split()[2]
            data['lat_s'] = lines_10[4].split()[5]
            data['lon_w'] = lines_10[5].split()[2]
            data['lon_e'] = lines_10[5].split()[5]
            data['geo_lat'] = lines_10[0].split()[5].replace(',', '')
            data['geo_lon'] = lines_10[0].split()[8].replace(')', '')

            data_raw = np.loadtxt(in_file, skiprows=10, dtype={
                'names': ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7'),
                'formats': ('S8', 'S8', 'S8', 'f4', 'f4', 'f4', 'f4')})

            if data_raw.size != 0:
                data['hms_s_s1'] = data_raw['d2']
                data['lat_s_s1'] = data_raw['d4']
                data['lon_s_s1'] = data_raw['d5']
                data['hms_e_s1'] = data['d3']
                data['lat_e_s1'] = data['d6']
                data['lon_e_s1'] = data['d7']

                data['hms_s_s2'] = data['hms_s_s1']
                data['lat_s_s2'] = data['lat_s_s1']
                data['lon_s_s2'] = data['lon_s_s1']
                data['hms_e_s2'] = data['hms_e_s1']
                data['lat_e_s2'] = data['lat_e_s1']
                data['lon_e_s2'] = data['lon_e_s1']

        else:
            raise KeyError('Cant handle this file type： {}'.format(file_type))
        return data


if __name__ == '__main__':
    # ################# test ReadOrbitCrossFile ################
    # LEO_AREA
    # leo_area_name = 'cross/AQUA_australia_LEO_AREA_20171221.txt'
    # read_data = ReadOrbitCrossFile.read_cross_file(leo_area_name, 'leo_area')

    # LEO_LEO
    # leo_leo_name = 'cross/FENGYUN-3D_NPP_LEO_LEO_20180901.txt'
    # read_data = ReadOrbitCrossFile.read_cross_file(leo_leo_name, 'leo_leo')

    # LEO_FIX
    leo_fix_name = 'cross/AQUA_FIX_LEO_FIX_20181101.txt'
    read_data = ReadOrbitCrossFile.read_cross_file(leo_fix_name, 'leo_fix')

    # GEO_LEO
    # geo_leo_name = 'cross/FENGYUN-2F_METOP-A_GEO_LEO20181101.txt'
    # read_data = ReadOrbitCrossFile.read_cross_file(geo_leo_name, 'geo_leo')

    keys = read_data.keys()
    keys.sort()
    for data_name in keys:
        print data_name
        print read_data[data_name]
    # ################# test ReadOrbitCrossFile ################
