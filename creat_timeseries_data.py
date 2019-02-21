#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/19
@Author  : AnNing
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd


def create_timeseries_data():
    date_start = datetime.now() - relativedelta(years=5)
    ints = np.random.randint(1, 3, 1000)
    l1 = list()
    date_tmp = None
    for i in ints:
        if date_tmp is None:
            date_tmp = date_start
        date_tmp = date_tmp + relativedelta(days=int(i))
        l1.append(date_tmp.strftime('%Y%m%d'))
    data1 = ints

    ints = np.random.randint(1, 3, 1000)
    date_tmp = None
    l2 = list()
    for i in ints:
        if date_tmp is None:
            date_tmp = date_start
        date_tmp = date_tmp + relativedelta(days=int(i))
        l2.append(date_tmp.strftime('%Y%m%d'))
    data2 = ints

    df1 = pd.DataFrame({'date': l1, 'value': data1})
    df2 = pd.DataFrame({'date': l2, 'value': data2})

    df1.to_csv('test_data/data1.xsl', index=False)
    df2.to_csv('test_data/data2.xsl', index=False)


if __name__ == '__main__':
    create_timeseries_data()
