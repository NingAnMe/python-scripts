#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/15
@Author  : AnNing
"""
import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

import h5py
import numpy as np

from DV.dv_map import dv_map
from DV.dv_plt import dv_hist, add_colorbar_horizontal
from DV.dv_plt import get_DV_Font, add_ax, plt

from lib_gsics.lib_hdf5 import merge_dict_data

TIME_TEST = True  # 时间测试开关
DEBUG = True  # DEBUG 开关

fy4_lon_lat_kdtree_pickle = 'fy4_lon_lat_kdtree.pickle'
fy4_lon_lat_pickle = 'fy4_lon_lat.pickle'


def main(ymd, dtype='TEST'):
    """
    :param dtype:
    :param ymd: (str)
    :return:
    """
    # ######################## 初始化 ###########################
    # ######################## 开始处理 ###########################
    # ######################## 加载数据 ###########################
    proj_dirs = {'YW': '/home/gsics/nas03/CMA_GSICS/',
                 'TEST': '/home/gsics/nas03/CMA_GSICS_TEST/'}
    proj_dir = proj_dirs[dtype]
    data_dir = 'ACOSP/SupportData/MatchedData/FY3D+MERSI_FY3D+HIRAS'

    dir_path = os.path.join(proj_dir, data_dir, ymd)
    file_names = os.listdir(dir_path)
    in_files = [os.path.join(dir_path, i) for i in file_names]
    in_files.sort()

    out_path = os.path.join(proj_dirs['TEST'], data_dir, 'Result', ymd)

    tbb_s1_all = dict()
    tbb_s2_all = dict()
    lon_all = list()
    lat_all = list()

    file_count = 0
    for in_file in in_files:
        if os.path.isfile(in_file):
            print "main: data file <<< {}".format(in_file)
            data = ReadCollocationData(in_file)
            tbb_s1 = data.get_tbb(sate='1')
            tbb_s2 = data.get_tbb(sate='2')
            lon = data.get_longitude(sate='1')
            lat = data.get_latitude(sate='1')

            merge_dict_data(tbb_s1_all, tbb_s1)
            merge_dict_data(tbb_s2_all, tbb_s2)
            lon_all = np.append(lon_all, lon)
            lat_all = np.append(lat_all, lat)
            file_count += 1
        else:
            continue
    if file_count <= 0:
        print "***Warning***Dont have enough file, file count is {}".format(file_count)
        return
    else:
        print '---INFO---File Count: {}'.format(file_count)

    with open(fy4_lon_lat_pickle) as f:
        fy4_lon_lat = pickle.load(f)

    with open(fy4_lon_lat_kdtree_pickle) as f:
        fy4_lon_lat_kdtree = pickle.load(f)

    for channel in tbb_s1_all:
        tbb_s1_channel = tbb_s1_all[channel]
        tbb_s2_channel = tbb_s2_all[channel]
        idx = np.logical_and(tbb_s1_channel > 0, tbb_s2_channel > 0)
        tbb_s1_channel = tbb_s1_channel[idx]
        tbb_s2_channel = tbb_s2_channel[idx]
        lon_channel = lon_all[idx]
        lat_channel = lat_all[idx]

        lon_lat = zip(lon_channel, lat_channel)
        dist, index = fy4_lon_lat_kdtree.query(lon_lat)

        idx = dist < 0.05
        index = index[idx]
        tbb_s1_channel = tbb_s1_channel[idx]
        tbb_s2_channel = tbb_s2_channel[idx]

        lon_lat_new = fy4_lon_lat[index]
        lon_channel_new = lon_lat_new[:, 0]
        lat_channel_new = lon_lat_new[:, 1]

        shortsat1 = 'FY3D'
        shortsat2 = 'FY3D'
        sensor1 = 'MERSI'
        sensor2 = 'HIRAS'
        ad_type = 'D'

        bias_tbb = tbb_s1_channel - tbb_s2_channel

        vmin = -2.
        vmax = 2.
        out_name = '%s+%s_%s+%s_GBAL_MAP_%s_%s_%s_Tbb_%s.png' % (
            shortsat1, sensor1, shortsat2, sensor2, ad_type, ymd, channel, dtype)
        opath = os.path.join(out_path, out_name)
        title = '%s %s BT  at %s %s (%s)' % (
            sensor1, sensor2, channel, ymd, ad_type)
        draw_fine_global_map(
            title, opath, lon_channel_new, lat_channel_new, bias_tbb, vmin, vmax, fmt='%0.2f',
            flag=1)
        print '>>>{}'.format(opath)


class ReadCollocationData(object):
    def __init__(self, in_file):
        self.in_file = in_file

    def get_tbb(self, sate):
        data_all = dict()
        with h5py.File(self.in_file, 'r') as hdf5:
            for key in hdf5.keys():
                if 'CH_' in key:
                    channel = key
                    dataset = 'S{}_FovTbbMean'.format(sate)
                    data_all[channel] = hdf5[channel][dataset][:]
        return data_all

    def get_longitude(self, sate):
        with h5py.File(self.in_file, 'r') as hdf5:
            dataset = 'S{}_Lon'.format(sate)
            data = hdf5[dataset][:]
            return data

    def get_latitude(self, sate):
        with h5py.File(self.in_file, 'r') as hdf5:
            dataset = 'S{}_Lat'.format(sate)
            data = hdf5[dataset][:]
            return data


def draw_fine_global_map(title, ofile, lons, lats, value, vmin, vmax, fmt='%d', flag=0):
    opath = os.path.dirname(ofile)
    if not os.path.isdir(opath):
        os.makedirs(opath)

    fig = plt.figure(figsize=(6, 4))  # 图像大小
    pos1 = [0.1, 0.3, 0.8, 0.6]
    ax1 = add_ax(fig, *pos1)
    p = dv_map(fig, ax=ax1)

    p.colormap = 'jet'
    p.delat = 30
    p.delon = 30
    #     p.colorbar_fmt = "%0.2f"
    p.show_countries = True
    #                 p.show_china = True
    #                 p.show_china_province = True
    p.show_line_of_latlon = True
    p.show_colorbar = False
    p.easyplot(
        lats, lons, value, vmin=vmin, vmax=vmax, markersize=1.5, marker='.')
    p.draw()
    # 直方图
    pos2 = [0.1, 0.15, 0.8, 0.1]
    ax2 = add_ax(fig, *pos2)
    p2 = dv_hist(fig, ax=ax2)
    p2.easyplot(
        value.reshape((-1,)), bins=512, cmap="jet", range=(vmin, vmax))
    p2.xlim_min = vmin
    p2.xlim_max = vmax
    p2.simple_axis(mode=0)
    p2.draw()

    # ColorBar
    pos3 = [0.1, 0.115, 0.8, 0.03]
    ax3 = add_ax(fig, *pos3)
    add_colorbar_horizontal(ax3, vmin, vmax, cmap="jet", fmt=fmt)

    # colorbar上打点
    if flag == 1:
        value = np.ma.masked_where(np.abs(value) > 3 * vmax, value)
        mean = np.ma.mean(value)
        print 'b', mean
    else:
        mean = np.ma.mean(value)

    precent = (mean - vmin) / (vmax - vmin)
    ax3.plot(precent, 0.5, 'ko', ms=5, zorder=5)

    font_mono = get_DV_Font()
    strlist = ["mean = %0.2f" % mean]
    add_annotate(ax2, strlist, 'left_top', font_mono)

    # 总标题
    fig.suptitle(title, fontproperties=p.font, size=14)

    p.savefig(ofile)


def add_annotate(ax, strlist, local, FONT_MONO, color="#000000", fontsize=11):
    """
    添加上方注释文字
    loc must be "left_top" or "right_top"
    or "left_bottom" or "right_bottom"
    格式 ["annotate1", "annotate2"]
    """
    if strlist is None:
        return
    xticklocs = ax.xaxis.get_ticklocs()
    yticklocs = ax.yaxis.get_ticklocs()

    x_step = (xticklocs[1] - xticklocs[0])
    x_toedge = x_step / 6.
    y_toedge = (yticklocs[1] - yticklocs[0]) / 6.

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    if local == "left_top":
        ax.text(xlim[0] + x_toedge, ylim[1] - y_toedge,
                "\n".join(strlist), ha="left", va="top", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)

    elif local == "right_top":
        ax.text(xlim[1] - x_toedge, ylim[1] - y_toedge,
                "\n".join(strlist), ha="right", va="top", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)

    elif local == "left_bottom":
        ax.text(xlim[0] + x_toedge, ylim[0] + y_toedge,
                "\n".join(strlist), ha="left", va="bottom", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)
    elif local == "right_bottom":
        ax.text(xlim[1] - x_toedge, ylim[0] + y_toedge,
                "\n".join(strlist), ha="right", va="bottom", color=color,
                fontsize=fontsize, fontproperties=FONT_MONO)
    else:
        return


if __name__ == '__main__':
    args = sys.argv[1:]
    YMD = args[0]
    YW_TEST = args[1]
    main(YMD, YW_TEST)
