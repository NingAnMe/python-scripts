#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/2
@Author  : AnNing
"""
import os
import sys
from PB.DRC.pb_drc_MVISR import ReadMvisrL1
from PB.pb_io import get_files_by_ymd
import numpy as np
from DV import dv_map
from configobj import ConfigObj
from lib_gsics.lib_gsics_path import get_pics_cfg_path


config_path = get_pics_cfg_path()
config_file = os.path.join(config_path, 'pics.cfg')
config = ConfigObj(config_file)
fix_sites = config['SITE_LIST']

lonlatlocation = []
for site in fix_sites:
    fix_lat = float(fix_sites[site][0])
    fix_lon = float(fix_sites[site][1])
    lonlatlocation.append((fix_lon, fix_lat, site))


def main(path, ymd):

    in_files = get_files_by_ymd(path, ymd, ymd, ext='.HDF', pattern_ymd='.*(\d{8})_\d{4}\.HDF')
    for f in in_files:
        plot_one_file_origin(f)
        plot_one_file(f)


def plot_one_file_origin(f):
    name = os.path.basename(f).replace('.HDF', '.PNG')
    data = ReadMvisrL1(f)
    lat = data.get_latitude_originality()
    lon = data.get_longitude_originality()
    print lat.shape
    count = np.full_like(lat, 1)
    out_file = os.path.join('global_plot_origin', name)
    title = name
    print f
    plot_map_project(lat, lon, count, out_file, title)


def plot_one_file(f):
    name = os.path.basename(f).replace('.HDF', '.PNG')
    data = ReadMvisrL1(f)
    lat = data.get_latitude()
    lon = data.get_longitude()
    count = np.full_like(lat, 1)
    out_file = os.path.join('global_plot', name)
    title = 'test'
    print f
    plot_map_project(lat, lon, count, out_file, title)


def plot_map_project(latitude, longitude,
                     count, out_file,
                     title=None, ptype=None,
                     vmin=None, vmax=None,
                     marker=None, markersize=None):
    if title is not None:
        title = title
    else:
        title = "Map"

    if vmin is not None:
        vmin = vmin

    if vmax is not None:
        vmax = vmax

    if marker is not None:
        marker = marker
    else:
        marker = 's'

    if markersize is not None:
        markersize = markersize
    else:
        markersize = 1

    p = dv_map.dv_map()

    p.easyplot(latitude, longitude, count, vmin=vmin, vmax=vmax,
               ptype=ptype, markersize=markersize, marker=marker)
    p.title = title
    p.add_landmark(lonlatlocation)
    p.savefig(out_file)
    print '>>> {}'.format(out_file)


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args[0], args[1])
