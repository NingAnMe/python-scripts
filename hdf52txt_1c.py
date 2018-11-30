#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/1
@Author  : AnNing
"""
from configobj import ConfigObj
from datetime import datetime
import os


import h5py
import numpy as np
import pandas as pd

from lib_gsics.lib_gsics_path import get_pics_cfg_path
from PB.pb_io import get_files_by_ymd

# HDF5 文件路径
IN_PATH = '/nas03/CMA_GSICS_TEST/Pics/SupportData/PreprocessingData/FY1C+MVISR/3_L2'

FIX_RANGE = os.path.basename(IN_PATH).split('_')[0]

# HDF5 文件名后缀
HDF_FILE_NAME_REG = '.H5'

# 输出路径
OUT_PATH = '/nas03/CMA_GSICS_TEST/Pics/SupportData/ExtractTXT/FY1C+MVISR/3_L3'
# 输出文件名
OUT_FILE_NAME = 'FY1C+MVISR_{}_lon{:+08.3f}_lat{:+08.3f}_{}x{}.txt'

YMD_START = '0'  # 开始时间

YMD_END = '20020622222'  # 结束时间

DATASETS = {
    'RelativeAzimuth_avg': 'relA_avg',
    'SensorZenith_avg': 'senZ_avg',
    'SolarZenith_avg': 'solZ_avg',
    'RelativeAzimuth_std': 'relA_std',
    'SensorZenith_std': 'senZ_std',
    'SolarZenith_std': 'solZ_std',
    'Timestamp_avg': 'Time',
}  # 外层数据集的名字,留空为全部,使用原名

CHANNEL_DATASETS = {
    'DN_avg': None,
    'DN_std': None,
    'SV_avg': None,
    'SV_std': None,
    'K0_avg': None,
    'K1_avg': None,
}  # 通道内数据集的名字,留空为全部,使用原名


def extract_fix():

    config_path = get_pics_cfg_path()
    config_file = os.path.join(config_path, 'pics.cfg')
    config = ConfigObj(config_file)
    fix_sites = config['SITE_LIST']

    all_files = get_files_by_ymd(IN_PATH, YMD_START, YMD_END, ext=HDF_FILE_NAME_REG)

    file_count_result = {}

    for site in fix_sites:
        fix_lat = float(fix_sites[site][0])
        fix_lon = float(fix_sites[site][1])
        in_files = []
        for f in all_files:
            if (site + '.') in f:
                in_files.append(f)
        file_count = len(in_files)
        print 'Find file count: {} {}'.format(site, file_count)
        file_count_result[site] = file_count
        if file_count <= 0:
            continue
        out_file_name = OUT_FILE_NAME.format(site, fix_lat, fix_lon, FIX_RANGE, FIX_RANGE)
        out_file = os.path.join(OUT_PATH, out_file_name)
        hdf52txt(in_files, out_file, DATASETS, CHANNEL_DATASETS)

    keys = file_count_result.keys()
    keys = sorted(keys)
    for k in keys:
        print '{:15} Day Count = {}'.format(k, file_count_result[k])


def hdf52txt(in_files, out_file, datasets=None, channel_datasets=None):

    hdf5_data = read_hdf5_files(in_files)

    if hdf5_data is None or not hdf5_data:
        return

    # 过滤并对数据集名字进行替换
    if datasets:
        filter_and_rename_dataset(hdf5_data, datasets)
    if channel_datasets:
        filter_and_rename_channel_dataset(hdf5_data, channel_datasets)

    # 将Timestamp转为ymd

    if 'Time' in hdf5_data:
        timestamp = hdf5_data.pop('Time')

        ymd, hm = timestamp2ymd_hm(timestamp)

        hdf5_data['YMD'] = ymd
        hdf5_data['HHMM'] = hm

        channel_data_to_txt(hdf5_data, out_file)


def read_hdf5_files(in_files):
    in_files = sorted(in_files)

    for in_file in in_files:
        if not os.path.isfile(in_file):
            print '***WARNING***File is not exist: {}'.format(in_file)
            in_files.pop(in_file)
    file_count = len(in_files)
    print '---INFO--- All file count: {} ---INFO'.format(file_count)
    if file_count <= 0:
        return

    result = dict()
    for in_file in in_files:
        print 'read <<< {}'.format(in_file)
        try:
            hdf5_data = read_hdf5(in_file)
            merge_dict_data(result, hdf5_data)
        except:
            print '***WARNING***Read data error: {}'.format(in_file)

    if not result:
        print '***ERROR***Dont merge any data.'
        return
    return result


def timestamp2ymd_hm(timestamp):
    date = map(datetime.utcfromtimestamp, timestamp)
    ymd = [d.strftime('%Y%m%d') for d in date]
    hm = [d.strftime('%H%M') for d in date]
    return ymd, hm


def filter_and_rename_dataset(data, datasets):
    if not datasets:
        return
    keys = data.keys()
    keys = [k for k in keys if 'CH' not in k]
    for dataset in keys:
        if dataset not in datasets:
            del data[dataset]
        elif datasets[dataset] is not None:
            data[datasets[dataset]] = data.pop(dataset)
        else:
            continue


def filter_and_rename_channel_dataset(data, channel_datasets):
    if not channel_datasets:
        return
    keys = data.keys()
    keys = [k for k in keys if 'CH' in k]
    for channel in keys:
        group = data[channel]
        filter_and_rename_dataset(group, channel_datasets)


def read_hdf5(in_file):
    """
    :param in_file:
    :return:
    """
    datas = {}
    with h5py.File(in_file, 'r') as hdf5:
        for key in hdf5:
            if type(hdf5[key]).__name__ == 'Group':
                group_name = key
                if group_name not in datas:
                    datas[group_name] = {}
                group_data = hdf5[key]
                for dataset_name in group_data:
                    data = group_data[dataset_name].value
                    # 处理
                    datas[group_name][dataset_name] = data
            else:
                dataset_name = key
                data = hdf5[dataset_name].value
                # 处理
                datas[dataset_name] = data
    return datas


def merge_dict_data(dict_data1, dict_data2):
    """
    将 data2 添加到 data1
    :param dict_data1: (dict)
    :param dict_data2: (dict)
    :return: data_shape = (1, n)
    """
    if not isinstance(dict_data1, dict) or not isinstance(dict_data2, dict):
        raise TypeError('Data is not dict type')
    for channel_name in dict_data2:
        if channel_name not in dict_data1:
            dict_data1[channel_name] = dict_data2[channel_name]
        else:
            if 'CH' in channel_name:
                merge_dict_data(dict_data1[channel_name], dict_data2[channel_name])
            else:
                data1 = dict_data1[channel_name]
                data2 = dict_data2[channel_name]
                channel_data = np.append(data1, data2)
                dict_data1[channel_name] = channel_data


def channel_data_to_txt(dict_data, out_file):
    if not dict_data:
        raise ValueError
    new_data = dict()

    for key in dict_data.keys():
        if not isinstance(dict_data[key], dict):
            dataset = key
            new_data[dataset] = dict_data[dataset]
        else:
            channel = key
            channel_data = dict_data[channel]
            for dataset in channel_data.keys():
                name = '{}_{}'.format(channel, dataset)
                new_data[name] = channel_data[dataset]

            time = dict_data['YMD']
            k2 = np.zeros(len(time), dtype=np.float)
            name = '{}_K2_avg'.format(channel)
            new_data[name] = k2

    df = pd.DataFrame(new_data)

    columns = ['YMD', 'HHMM',
               'CH_01_DN_avg', 'CH_01_DN_std', 'CH_01_SV_avg', 'CH_01_SV_std',
               'CH_01_K0_avg', 'CH_01_K1_avg', 'CH_01_K2_avg',

               'CH_02_DN_avg', 'CH_02_DN_std', 'CH_02_SV_avg', 'CH_02_SV_std',
               'CH_02_K0_avg', 'CH_02_K1_avg', 'CH_02_K2_avg',

               'CH_03_DN_avg', 'CH_03_DN_std', 'CH_03_SV_avg', 'CH_03_SV_std',
               'CH_03_K0_avg', 'CH_03_K1_avg', 'CH_03_K2_avg',

               'CH_04_DN_avg', 'CH_04_DN_std', 'CH_04_SV_avg', 'CH_04_SV_std',
               'CH_04_K0_avg', 'CH_04_K1_avg', 'CH_04_K2_avg',

               'senZ_avg', 'senZ_std', 'solZ_avg', 'solZ_std', 'relA_avg', 'relA_std']

    print df.describe()

    out_path = os.path.dirname(out_file)
    if out_path and not os.path.isdir(out_path):
        os.makedirs(out_path)

    out_file = os.path.splitext(out_file)[0]

    df.to_csv(out_file + '.txt', header=True, index=False, sep='\t', mode='w', columns=columns)
    print '>>> {}'.format(out_file + '.txt')
    df.to_csv(out_file + '.csv', header=True, index=False, mode='w', columns=columns)
    print '>>> {}'.format(out_file + '.csv')


if __name__ == '__main__':
    extract_fix()
