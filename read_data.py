#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/7/27 15:27
@Author  : AnNing
"""
import os
from datetime import datetime
import h5py
import numpy as np
from PB.DRC.congrid import congrid
from PB.pb_name import nameClassManager
from PB.pb_sat import planck_r2t


class ReadL1Data(object):
    """
    读取 L1 数据
    """
    def __init__(self):
        self.error = False

        self.ymd = None
        self.hm = None

        # 文件属性使用字典
        self.file_attr = None
        self.attr = None
        # 分通道写HDF用字典
        # self.DN = {'channel_name1': data1,}
        self.DN = None
        self.SV = None
        self.REF = None
        self.RAD = None
        self.TBB = None
        self.BB = None

        # 不分通道写HDF用列表或者常量
        # self.Height = [1, 2, 3] or self.Height = 4
        self.Height = None
        self.LandCover = None
        self.LandSeaMask = None
        self.Latitude = None
        self.Longitude = None
        self.SensorAzimuth = None
        self.SensorZenith = None
        self.SolarAzimuth = None
        self.SolarZenith = None
        self.RelativeAzimuth = None
        self.Time = None

    @staticmethod
    def mask_invalid_data(data, valid_range):
        data = np.ma.masked_less(data, valid_range[0])
        data = np.ma.masked_greater(data, valid_range[1])
        return data

    def read_hdf5_dataset_mask_invalid_data(self, dataset):
        valid_range = dataset.attrs['valid_range']
        data_masked = self.mask_invalid_data(dataset.value, valid_range)

        intercept = dataset.attrs['Intercept']
        slope = dataset.attrs['Slope']
        data = data_masked * slope + intercept
        return data


class ReadHDF5(object):
    """
    读取 HDF5 文件数据，以字典形式分级储存数据和属性
    self.data={'group': {'dataset1': data1,
                        'dataset2': data2,},
                'dataset3': data3,}
    read_hdf5()
    read_groups()
    read_datasets()
    read_group()
    read_datasets()
    """
    def __init__(self, in_file):
        self.error = False
        self.file_path = in_file
        self.dir_path = os.path.dirname(in_file)
        self.file_name = os.path.basename(in_file)

        self.ymd = None
        self.hm = None

        self.data = dict()
        self.file_attr = self._read_file_attr()
        self.data_attr = dict()

    def read_hdf5(self, datasets=None, groups=None):
        """
        :param datasets: [str] 需要读取的数据集
        :param groups: [str] 需要读取的数据组
        :return:
        """
        if self.error:
            return
        if datasets:
            self.read_datasets(datasets)
        if groups:
            self.read_groups(groups)
        if datasets is None and groups is None:
            self.read_all()

    def read_all(self):
        """
        读取HDF5文件内所有的dataset数据与dataset属性
        :return:
        """
        if self.error:
            return
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for item in hdf5_file:
                if type(hdf5_file[item]).__name__ == 'Group':
                    hdf5_group = hdf5_file[item]
                    self.read_group(hdf5_group)
                else:
                    hdf5_dataset = hdf5_file[item]
                    self.read_dataset(hdf5_dataset)

    def read_groups(self, groups):
        """
        读取HDF5文件内多个group的数据和dataset属性
        :param groups: [str] 需要读取的数据组
        :return:
        """
        if self.error:
            return
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for group in groups:
                hdf5_group = hdf5_file[group]
                self.read_group(hdf5_group)

    def read_datasets(self, datasets):
        """
        读取HDF5文件内多个dataset的数据和dataset属性
        :param datasets: [str] 需要读取的数据集
        :return:
        """
        if self.error:
            return
        with h5py.File(self.file_path, 'r') as hdf5_file:
            for dataset in datasets:
                hdf5_dataset = hdf5_file[dataset]
                self.read_dataset(hdf5_dataset)

    def read_group(self, hdf5_group):
        """
        读取HDF5文件内一个group的数据和dataset属性
        :param hdf5_group:
        :return:
        """
        if self.error:
            return
        for item in hdf5_group:
            if type(hdf5_group[item]).__name__ == 'Group':
                hdf5_group = hdf5_group[item]
                self.read_group(hdf5_group)
            else:
                hdf5_dataset = hdf5_group[item]
                self.read_dataset(hdf5_dataset)

    def read_dataset(self, hdf5_dataset):
        """
        读取HDF5文件内一个dataset的数据和dataset属性
        :param hdf5_dataset:
        :return:
        """
        if self.error:
            return
        dataset_path = hdf5_dataset.name.split('/')
        dataset_name = dataset_path.pop()
        data, attr = self._create_data_attr_dict(dataset_path)
        data[dataset_name] = hdf5_dataset.value
        attr[dataset_name] = self.read_dataset_attr(hdf5_dataset)

    def _create_data_attr_dict(self, dataset_path):
        """
        :param dataset_path: [str]
        :return: (dict, dict)
        """
        data = self.data
        attr = self.data_attr
        for i in dataset_path:
            if not i:
                continue
            if i in data:
                data = data[i]
                attr = attr[i]
                continue
            else:
                data[i] = {}
                attr[i] = {}
                data = data[i]
                attr = attr[i]
        return data, attr

    def _read_file_attr(self):
        """
        读取HDF5文件的属性
        :return:
        """
        d = {}
        try:
            with h5py.File(self.file_path, 'r') as hdf5_file:
                for k, v in hdf5_file.attrs.items():
                    d[k] = v
        except Exception as why:
            print why
            self.error = True
        return d

    @staticmethod
    def read_dataset_attr(dataset):
        """
        读取HDF5文件dataset的属性
        :return:
        """
        d = {}
        for k, v in dataset.attrs.items():
            d[k] = v
        return d


if __name__ == '__main__':
    g_test_file = r'D:\nsmc\fix_data\FY3ABC\FY3A_VIRRX_GBAL_L1_20131206_1355_1000M_MS.HDF'
    name_class = nameClassManager()
    g_info = name_class.getInstance(g_test_file)
    g_sec = int((g_info.dt_s - datetime(1970, 1, 1, 0, 0, 0)).total_seconds())
    print g_sec
