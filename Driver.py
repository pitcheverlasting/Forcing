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
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec')
varname = ('Tmax', 'Tmin', 'Rs', 'Wind', 'RH', 'Prec')

glat = 292
glon = 296
styr = 1948
edyr = 2007
dates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

## convert daily data into single file for detrending
flag_data = 2
if flag_data == 1:
	for var in forcing:
		data = []
		for year in xrange(styr, edyr+1):
			if calendar.isleap(year):
				nd = 366
			else:
				nd = 365
			stdy = datetime.date(year, 1, 1)
			for d in xrange(0, nd):
				curdy = stdy + dt.timedelta(d)
				data.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(1, glat, glon))
		data = vstack(data)
		data.dump('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))


## detrend data time series for each point
if flag_data == 2:
	for var in forcing:
		print var
		if not os.path.exists('%s%s' % (workspace, var)):
			os.makedirs('%s%s' % (workspace, var))
		for lon in xrange(0, glon):
			for lat in xrange(0, glat):
				timeseries = []
				for year in xrange(styr, edyr+1):
					if calendar.isleap(year):
						nd = 366
						print lon, year
					else:
						nd = 365
					stdy = datetime.date(year, 1, 1)
					for d in xrange(0, nd):
						curdy = stdy + dt.timedelta(d)
						timeseries.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(glat, glon)[lat, lon])

				timeseries = array(timeseries)

				# 1st: use detrend in mlab
				data_detrend = mlab.detrend_linear(timeseries)
				mean = mean(timeseries)
				timeseries_update = data_detrend + mean
				timeseries_update.dump('%s%s/pgf_%s_detrend_%s-%s' %(workspace, var, var, lat, lon))
				del timeseries_update, timeseries, data_detrend

	# ts = Series(data_detrend, index=dates)
	# print ts[dt.datetime(1948, 12, 29):dt.datetime(1949, 1, 4)]
	#		data = load('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))

	# growing season??
