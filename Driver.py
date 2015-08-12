__author__ = 'pitch'

"""Counterfactual climate datasets forcing"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. extract point data time series
# 	2. detrend
#   3. add counterfactual trend
##============================================================================================

## import library
##---------------
import sys, os, glob, fnmatch, gc
# time handling
import time, calendar
import datetime as dt
from pandas.tseries.offsets import Day
import pandas as pd
from netCDF4 import Dataset
from pandas import Series, DataFrame
# tool
import numpy as np
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec')
varname = ('Tmax', 'Tmin', 'Rs', 'Wind', 'RH', 'Prec')

glat = 292
glon = 296
styr = 1948
edyr = 1948
dates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

data = fromfile('%s.bin' % (datadir),'float32')
for lon in xrange(0, glon):
    for lat in xrange(0, glat):
        data_detrend[lon, lat] = mlab.detrend_linear(data[lon, lat])
        ts = Series(data_detrend, index=dates)
# print ts[dt.datetime(1948, 12, 29):dt.datetime(1949, 1, 4)]
#
# growing season??
