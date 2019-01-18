#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/1/15
@Author  : AnNing

操作 HDF5 的样例程序

绘图样例程序
"""
import sys
import h5py
import numpy as np


def main():
    """
    不带输入参数的程序
    :return:
    """
    # 数据读取
    in_file_ = r'D:/dir/in_file.h5'
    datas_ = read_hdf5_all(in_file_)

    # 数据写入
    out_file_ = r'D:/dir/out_file.h5'
    write_hdf5_and_compress(out_file_, datas_)


# def main(in_file, out_file):
#     """
#     带输入输出参数的程序
#     :param in_file:
#     :param out_file:
#     :return:
#     """
#     # 数据读取
#     datas_ = read_hdf5_all(in_file_)
#     # 数据写入
#     write_hdf5_and_compress(out_file_, datas_)


def read_hdf5_all(in_file):
    """
    读取HDF5文件内的所有数据，仅支持两层
    :param in_file:
    :return: 数据集内所有数据
    """
    datas = {}
    with h5py.File(in_file, 'r') as hdf5:
        for key in hdf5:
            # 读取Group
            if type(hdf5[key]).__name__ == 'Group':
                group_name = key
                if group_name not in datas:
                    datas[group_name] = {}
                group_data = hdf5[key]
                for dataset_name in group_data:
                    data = group_data[dataset_name].value  # 读取出来的数据
                    # 处理
                    datas[group_name][dataset_name] = data
            # 读取 Dataset
            else:
                dataset_name = key
                data = hdf5[dataset_name].value
                # 处理
                datas[dataset_name] = data
    return datas


def write_hdf5_and_compress(out_file, datas):
    """
    将数据写入HDF5文件
    :param out_file: (str)
    :param datas: (dict)
    :return:
    """
    if not datas:
        return
    compression = 'gzip'  # 压缩算法种类
    compression_opts = 5  # 压缩等级
    shuffle = True
    with h5py.File(out_file, 'w') as hdf5:
        for key in datas:
            # 写入 Group
            if isinstance(datas[key], dict):
                group_name = key
                group_data = datas[key]
                if isinstance(group_data, dict):
                    for dataset_name in group_data:
                        data = group_data[dataset_name]
                        # 处理
                        hdf5.create_dataset('/{}/{}'.format(group_name, dataset_name),
                                            dtype=np.float32, data=data, compression=compression,
                                            compression_opts=compression_opts,
                                            shuffle=shuffle)
            # 写入 Dataset
            else:
                dataset_name = key
                data = datas[dataset_name]
                # 处理
                hdf5.create_dataset(dataset_name, data=data, compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle)
    print('>>> {}'.format(out_file))


# ######################## 不带命令行参数的程序入口 ##############################
if __name__ == '__main__':
    main()


# # ######################## 带命令行参数的程序入口 ##############################
# if __name__ == "__main__":
#     # 获取程序参数接口
#     ARGS = sys.argv[1:]
#     HELP_INFO = \
#         u"""
#         [arg1]：yaml_path
#         [example]： python app.py arg1
#         """
#     if "-h" in ARGS:
#         print HELP_INFO
#         sys.exit(-1)
#
#     if len(ARGS) != 1:
#         print HELP_INFO
#         sys.exit(-1)
#     else:
#         ARG1 = ARGS[0]
#         main(ARG1)
