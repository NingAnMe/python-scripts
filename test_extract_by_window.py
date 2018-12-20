#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/12/12
@Author  : AnNing
"""
import numpy as np


def extract_data_by_window(data=None, row_col_index=None, window_size=None):
    """
    以某行列号为中心，在二维矩阵中提取窗口大小的数据
    :param data: (可以被np.array()支持的数据) 二维数据
    :param row_col_index: (row_int, col_int)
    :param window_size: (int)
    :return:
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    data_new = np.zeros((window_size, window_size), dtype=np.float32)
    data_new.fill(np.nan)
    data = np.array(data)
    x = (window_size - 1) // 2
    y = window_size - x

    row_min = row_col_index[0] - x
    row_max = row_col_index[0] + y
    col_min = row_col_index[1] - x
    col_max = row_col_index[1] + y

    if row_min > 0:
        row_min_tem = row_min
    else:
        row_min_tem = 0
    if col_min > 0:
        col_min_tem = col_min
    else:
        col_min_tem = 0

    data_window = data[row_min_tem:row_max, col_min_tem:col_max]

    if len(data_window) <= 0:
        return data_new

    shape_data_window = data_window.shape
    # 如果开始的row或者col小于0，要处理开始和结束的行列号，不再是从（0,0）开始覆盖
    if row_min < 0:
        row_start = abs(row_min)
    else:
        row_start = 0
    if col_min < 0:
        col_start = abs(col_min)
    else:
        col_start = 0
    row_end = row_start + shape_data_window[0]
    col_end = col_start + shape_data_window[1]
    try:
        data_new[row_start:row_end, col_start:col_end] = data_window
    except Exception as why:
        print why
    return data_new


if __name__ == '__main__':
    t_data = np.arange(1000000).reshape(1000, 1000)
    t = extract_data_by_window(t_data, (127, 127), 256)

    print t.shape