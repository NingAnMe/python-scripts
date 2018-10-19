#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/19
@Author  : AnNing
"""
import numpy as np
import pandas as pd

d = pd.read_table('test1.txt', header=None)
data = d[5]
data1 = data[0:12]
data2 = data[12:24]
data3 = data[24:]

new_data = np.array([])
for x1, x2, x3 in zip(data1, data2, data3):
    x4 = (x1+x2+x3) / 3
    print x1, x2, x3, x4
    new_data = np.append(new_data, x4)

print new_data

step = 1
p = 1
for i in xrange(0, len(new_data-step)):
    gain = new_data[i]
    p = p * (new_data[i] / 100 + 1)
    print gain, p


# data_greater_zero = data[data>0]
# data_lower_zero = data[data<0]
# for data in [data_greater_zero, data_lower_zero]:
#     print len(data)
#     print np.min(data)
#     print np.max(data)
#     print np.mean(data)
#     print np.std(data)
#     print
