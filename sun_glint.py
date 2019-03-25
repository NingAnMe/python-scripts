#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/3/25
@Author  : AnNing
计算耀斑角
"""
import numpy as np


def sun_glint_cal(obs_a, obs_z, sun_a, sun_z):
    """
    计算太阳耀斑角
    :param obs_a: 卫星方位角 Azimuth
    :param obs_z: 卫星天顶角 Zenith
    :param sun_a: 太阳方位角 Azimuth
    :param sun_z: 太阳天顶角 Zenith
    :return: glint： 耀斑角
    """
    ti = np.deg2rad(sun_z)
    tv = np.deg2rad(obs_z)
    phi = np.deg2rad(sun_a - obs_a)
    cos_phi = np.cos(phi)

    cos_tv = np.cos(tv)
    cos_ti = np.cos(ti)
    sin_tv = np.sin(tv)
    sin_ti = np.sin(ti)

    cos_res = cos_ti * cos_tv - sin_ti * sin_tv * cos_phi
    v_array_min = np.vectorize(array_min)

    cos_min = v_array_min(cos_res, 1.0)

    v_array_max = np.vectorize(array_max)
    cos_max = v_array_max(cos_min, -1)
    res = np.arccos(cos_max)
    glint = np.rad2deg(res)

    return glint


def array_min(array_a, b):
    return min(array_a, b)


def array_max(array_a, b):
    return max(array_a, b)
