#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/1/24
@Author  : AnNing
"""
import numpy as np


def get_box(lats, lons):
    lat_min = np.min(lats)
    lat_max = np.max(lats)

    lons_min = np.min(lons)
    lons_max = np.max(lons)

    lat_s = 90
    for i in xrange(-90, 91, 30):
        if i >= lat_max:
            lat_s = i
            break

    lat_n = -90
    for i in xrange(90, -91, -30):
        if i <= lat_min:
            lat_n = i
            break

    lon_w = -180
    for i in xrange(180, -181, -30):
        if i <= lons_min:
            lon_w = i
            break

    lon_e = 180
    for i in xrange(-180, 181, 30):
        if i >= lons_max:
            lon_e = i
            break

    return [lat_s, lat_n, lon_w, lon_e]
