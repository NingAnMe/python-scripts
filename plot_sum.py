#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
编写脚本
脚本运行输入： dir_path: (str)  例如： python plot_sum.py test_data

脚本功能：
1、通过输入的目录，读取 data1 和 data2 的数据，数据格式为 date 和 value, 且 date 已经排序
2、将data1和data2中具有相同 date 的数据进行求和
3、绘制折线图，x 为 date， y 为 sum

样例：
数据集1
date value
20140220,1
20140223,2
20140224,1

数据集2
date value
20140220,1
20140221,1
20140224,1

结果
date value
20140220,2
20140224,2

"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    pass


if __name__ == '__main__':
    argv = sys.argv
    main()
