#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/28
@Author  : AnNing
"""
import numpy as np
import pandas as pd


data = pd.read_csv('RoomQs.csv')

print(data)

x = list(range(0, 23*3600+1, 3600))
y2 = list(range(0, 24*3600, 300))

result = None

for i in range(0, 10):
    y = data.iloc[:, i]
    r = np.interp(y2, x, y).reshape((288, 1))
    if result is None:
        result = r
    else:
        result = np.concatenate((result, r), axis=1)

df = pd.DataFrame(result)
df.to_csv('Result.csv')