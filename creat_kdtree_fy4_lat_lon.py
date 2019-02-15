#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/15
@Author  : AnNing
"""
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

import h5py
import numpy as np
from scipy.spatial import cKDTree
from lib_gsics.lib_gsics_plot_core import plot_map

def main():
    fy4_lon_lat_lut = 'FY4X_LON_LAT_LUT.H5'
    fy4_lon_lat_kdtree_pickle = 'fy4_lon_lat_kdtree.pickle'
    fy4_lon_lat_pickle = 'fy4_lon_lat.pickle'
    with h5py.File(fy4_lon_lat_lut, 'r') as hdf5:
        lon = hdf5.get('Longitude')[:]
        lat = hdf5.get('Latitude')[:]

    lon = lon.ravel()
    lat = lat.ravel()

    idx = np.logical_and(lon != -639, lat != -999)
    lon = lon[idx] + 104.7
    lat = lat[idx]

    lon_lat = np.dstack([lon, lat])[0]
    print lon_lat.shape

    fy4_lon_lat_kdtree = cKDTree(lon_lat)

    with open(fy4_lon_lat_kdtree_pickle, 'wb') as f:
        pickle.dump(fy4_lon_lat_kdtree, f)

    with open(fy4_lon_lat_pickle, 'wb') as f:
        pickle.dump(lon_lat, f)

    if os.path.isfile(fy4_lon_lat_kdtree_pickle):
        with open(fy4_lon_lat_kdtree_pickle) as f:
            fy4_lon_lat_kdtree_load = pickle.load(f)

            points = lon_lat[:100]

            result = fy4_lon_lat_kdtree_load.query(points)
            print(result)


if __name__ == '__main__':
    main()
