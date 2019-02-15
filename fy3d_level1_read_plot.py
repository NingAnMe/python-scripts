#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/1/18
@Author  : AnNing

样例程序，读取FY3D的 DN 值数据，常用操作数据的方法
绘制灰度图、真彩图、折线图、散点图，直方图

看不懂的地方就用type() 和 print()
看一眼就懂了
print(type(something))
"""
import os

import h5py
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance


def main():
    # ---------- 设置读取的文件 ----------
    in_dir = r'D:\nsmc\L1\FY3D'  # 文件目录名 （查 r 的作用）
    filename = 'FY3D_MERSI_GBAL_L1_20180110_1230_1000M_MS.HDF'  # 文件名
    in_file = os.path.join(in_dir, filename)  # （查 os.path.join 函数作用）
    print('1')
    print(in_file)

    out_dir = r'result'  # 输出目录
    if not os.path.isdir(out_dir):  # 如果输出目录不存在，则创建输出目录
        os.mkdir(out_dir)

    # ---------- 读取 DN 值 ----------
    data_dn = read_fy3d_level1_dn(in_file)
    print('3')
    print(data_dn.keys())
    print(type(data_dn))

    # ---------- 查看1通道的DN值数据 ----------
    dn_channel1 = data_dn['CH_01']
    print('4')
    print(type(dn_channel1))  # 数据类型
    print(dn_channel1.shape)  # 数据形状
    print(dn_channel1)  # 数据

    # ---------- 绘制伪彩图 ----------
    out_pic1 = os.path.join(out_dir, 'out_pic1.png')
    plt.imshow(dn_channel1)

    plt.savefig(out_pic1)
    plt.close()

    # ---------- 绘制灰度图 ----------
    out_pic2 = os.path.join(out_dir, 'out_pic2.png')
    plt.imshow(dn_channel1, cmap='Greys')

    plt.savefig(out_pic2)
    plt.close()

    # ---------- 绘制真彩图 ----------
    dn_channel2 = data_dn.get('CH_02')  # 查字典操作 .get 和 [] 的区别
    dn_channel3 = data_dn['CH_03']

    r = normal255int8(dn_channel3)
    g = normal255int8(dn_channel2)
    b = normal255int8(dn_channel1)

    img_rgb = np.stack([r, g, b], axis=2)

    print(img_rgb.min())
    print(img_rgb.max())
    print(img_rgb.dtype)

    out_pic3 = os.path.join(out_dir, 'out_pic3.png')
    plt.imshow(img_rgb)

    plt.savefig(out_pic3)
    plt.close()

    # ---------- 使用 Image 绘制真彩图 ----------
    dn_channel2 = data_dn.get('CH_02')  # 查字典操作 .get 和 [] 的区别
    dn_channel3 = data_dn['CH_03']

    r = normal255int8(dn_channel3)
    g = normal255int8(dn_channel2)
    b = normal255int8(dn_channel1)

    imr = Image.fromarray(r, 'L')
    img = Image.fromarray(g, 'L')
    imb = Image.fromarray(b, 'L')
    im = Image.merge('RGB', (imr, img, imb))

    out_pic33 = os.path.join(out_dir, 'out_pic33.png')
    im.save(out_pic33)

    # 图像增强
    enh_bri = ImageEnhance.Brightness(im)
    brightness = 2
    image_brightened = enh_bri.enhance(brightness)

    out_pic34 = os.path.join(out_dir, 'out_pic34.png')
    image_brightened.save(out_pic34)

    # ---------- 绘制折线图 ----------
    out_pic4 = os.path.join(out_dir, 'out_pic4.png')
    data_oneline = dn_channel1[0]  # 第一行的数据
    plt.plot(data_oneline)

    plt.savefig(out_pic4)
    plt.close()

    # ---------- 绘制散点图 ----------
    out_pic5 = os.path.join(out_dir, 'out_pic5.png')
    data_oneline = dn_channel1[0]  # 第一行的数据
    x = np.arange(0, len(data_oneline))
    plt.scatter(x, data_oneline)

    plt.savefig(out_pic5)
    plt.close()

    # ---------- 绘制直方图 ----------
    out_pic6 = os.path.join(out_dir, 'out_pic6.png')
    data_oneline = dn_channel1[0]  # 第一行的数据
    plt.hist(data_oneline)

    plt.savefig(out_pic6)
    plt.close()

    # ---------- 常用数据操作 ----------
    data = data_dn['CH_01']
    print(data.shape)

    data_one_row = data[0]  # 第一行数据
    print(data_one_row.shape)
    data_one_col = data[:, 0]  # 第一列数据
    print(data_one_col.shape)

    data_one_point = data[0, 0]  # 第一个数据
    print(data_one_point)

    data_23_45 = data[1:3, 3:5]  # 第2-3行，4-5列的数据
    print(data_23_45.shape)

    data_greater_50 = data[data > 50]  # 大于 50 的数据
    print(data_greater_50.shape)

    data[data < 50] = 0.  # 将小于50的值重新赋值为0


def normal255int8(array):
    """
    小于 0 的值赋值为0，其他值归一化到 0-255
    :param array: ndarray
    :return: ndarray
    """
    array[array < 0] = 0
    data = (array - array.min()) / (array.max() - array.min())
    data = data * 255
    data = data.astype(np.uint8)
    return data


def read_fy3d_level1_dn(in_file):
    """
    读取 FY3D 的 DN 值
    :param in_file:
    :return: dict
    """
    # 读取 25 个通道的 DN 值
    data_dn = dict()  # 创建一个字典存放数据
    with h5py.File(in_file, 'r') as h5r:  # （查 with 打开文件的好处）
        print('2')
        print(h5r)  # 打开的HDF5文件
        print(h5r.keys())  # 内容

        ary_ch1_4 = h5r.get('/Data/EV_250_Aggr.1KM_RefSB')[:]
        ary_ch5_19 = h5r.get('/Data/EV_1KM_RefSB')[:]
        ary_ch20_23 = h5r.get('/Data/EV_1KM_Emissive')[:]
        ary_ch24_25 = h5r.get('/Data/EV_250_Aggr.1KM_Emissive')[:]
        vmin = 0  # 最小有效值
        vmax = 65000  # 最大有效值
        # 逐个通道处理
        channels = 25  # 一共25个通道的数据
        for i in range(channels):
            channel = 'CH_{:02d}'.format(i + 1)
            print(channel)
            if i < 4:
                k = i
                data_channel = ary_ch1_4[k]
                # 开始处理
            elif 4 <= i < 19:
                k = i - 4
                data_channel = ary_ch5_19[k]
            elif 19 <= i < 23:
                k = i - 19
                data_channel = ary_ch20_23[k]
            else:
                k = i - 23
                data_channel = ary_ch24_25[k]

            # 过滤无效值
            data_channel = data_channel.astype(np.float32)  # 转为 32 位浮点值
            invalid_index = np.logical_or(data_channel <= vmin, data_channel > vmax)
            data_channel[invalid_index] = 0.  # 将无效值赋值为 0
            data_dn[channel] = data_channel
    return data_dn


if __name__ == '__main__':
    main()
