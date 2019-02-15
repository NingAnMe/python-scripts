#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/15
@Author  : AnNing
"""
import os
import sys

import numpy as np
import pandas as pd

from PB.pb_time import time_block
from lib_gsics.lib_gsics_path import get_accurate_cfg_path
from lib_gsics.lib_accurate_read import ReadCombineData
from lib_gsics.lib_gsics_plot_core import plot_timeseries
from lib_gsics.lib_hdf5 import merge_dict_data
from lib_gsics.lib_initialize import load_yaml_file
from lib_gsics.lib_filter import has_empty_data_or_not_equal_length

TIME_TEST = True  # 时间测试开关
DEBUG = True  # DEBUG 开关


def main(ymd):
    """
    :param ymd: (str)
    :return:
    """
    # ######################## 初始化 ###########################
    # 加载接口文件
    print "main: interface file <<< {}".format(yaml_file)

    interface_config = load_yaml_file(yaml_file)
    i_pair = interface_config['INFO']['pair']  # 卫星+传感器 or 卫星+传感器_卫星+传感器（str）
    i_in_files = interface_config['PATH']['ipath']  # 待处理文件绝对路径列表（list）
    i_out_path = interface_config['PATH']['opath']  # 输出文件绝对路径（str）
    i_is_launch = interface_config['INFO']['is_launch']  # 是否发星来
    i_orbit = interface_config['INFO']['orbit']  # orbit
    i_ymd_start = interface_config['INFO']['ymd_s']
    i_ymd_end = interface_config['INFO']['ymd_e']

    # 加载应用配置
    config_path = get_accurate_cfg_path()
    config_file = os.path.join(config_path, '{}.plot'.format(i_pair))
    print "main: app config file <<< {}".format(config_file)

    app_config = load_yaml_file(config_file)
    a_timeseries_config = app_config['p03']

    # ######################## 开始处理 ###########################
    # ######################## 加载数据 ###########################
    dir_path_t = '/{}'
    dir_path = dir_path_t.format(ymd)
    file_names = os.listdir(dir_path)
    in_files = [os.path.join(dir_path, i) for i in file_names]
    in_files.sort()

    all_data = dict()
    file_count = 0
    for in_file in in_files:
        if os.path.isfile(in_file):
            print "main: data file <<< {}".format(in_file)

            file_count += 1
        else:
            continue
    if file_count <= 0:
        print "***Warning***Dont have enough file, file count is {}".format(file_count)
        return
    else:
        print '---INFO---File Count: {}'.format(file_count)
