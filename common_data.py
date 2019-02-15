#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/14
@Author  : AnNing
"""
import numpy as np
import pandas as pd


def get_common_data(data1, data2, date1, date2):
    df1 = pd.DataFrame(data={'date': date1, 'data1': data1})
    df2 = pd.DataFrame(data={'date': date2, 'data2': data2})
    df_merge = pd.merge(df1, df2, on='date')
    date_common = df_merge['date'].map(pd.Timestamp.to_pydatetime)
    date_common = [date.to_pydatetime() for date in date_common]

    date_common = np.array(date_common)
    bias_common = df_merge['data1'] - df_merge['data2']

    return date_common, bias_common
