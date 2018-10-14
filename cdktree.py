#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/8/2 10:40
@Author  : AnNing
"""

data_length = len(lons_lats)
dist_tem = 0.2
n = 1
for i in xrange(n):
    # 将原数据分为n份计算
    print i
    length_one = data_length / n
    data = lons_lats[i*length_one:(i+1)*length_one]

    ck = cKDTree(data)
    print 'start query'
    dist, index = ck.query([fix_point], 1)
    dist = dist[0]
    index = index[0]
    # index 还原为原数据的index
    index = index + length_one * i
    print 'dist: {}  index: {}'.format(dist, index)

    if dist <= dist_tem:
        dist_tem = dist
        self.fix_point_index = (idx[0][index], idx[1][index])
    else:
        continue

precision = 0.2  # sqrt(lat^2 + lon^2) - dist < precision，有效固定点
data = lons_lats
print 'start cKDTree'
print 'lon new min: {}'.format(lon_new.min())
print 'lon new max: {}'.format(lon_new.max())
print 'lat new.min: {}'.format(lat_new.min())
print 'lat new.max: {}'.format(lat_new.max())

ck = cKDTree(data)

fix_point = (fix_lon, fix_lat)
dist, index = ck.query([fix_point], 1)
dist = dist[0]
index = index[0]
print 'dist: {}  index: {}'.format(dist, index)

if dist <= precision:
    fix_point_index = (idx[0][index], idx[1][index])
