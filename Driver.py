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
import sys, os, gc
# time handling
import time, calendar
from pandas.tseries.offsets import Day
import pandas as pd
from netCDF4 import Dataset
from pandas import Series, DataFrame
# tool
from pylab import *
import IO, DataProcess
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec')

glat = 292
glon = 296
styr = 1948
edyr = 2010
stdy = datetime.datetime(styr, 1, 1)
eddy = datetime.datetime((edyr), 12, 31)
nt = (eddy - stdy).days + 1
nmon = (edyr - styr + 1) * 12

# Define region dimensions
dims = {}
dims['minlat'] = -34.875
dims['minlon'] = -18.875
dims['nlat'] = 292
dims['nlon'] = 296

dims['res'] = 0.250
dims['maxlat'] = dims['minlat'] + dims['res'] * (dims['nlat'] - 1)
dims['maxlon'] = dims['minlon'] + dims['res'] * (dims['nlon'] - 1)
dims['undef'] = -9.99e+08

## Aggregate monthly time series to calculate linear trend
types = ('ave', 'ave', 'ave', 'ave', 'ave', 'pre')
for i in xrange(0, len(forcing)):
	ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], styr, edyr)
	# initial month start day
	monst = stdy
	data_mon = []
	for j in xrange(0, nmon):
		# end day of the month
		moned = monst + relativedelta(months=1) - relativedelta(days=1)

		data = DataProcess.Extract_Data_Periodd_Average(monst, moned, 'open', ctl_out, varname[i], types[i])
		# Convert 2-d arrays to 3-d for stacking
		data_mon.append(data.reshape(1, glat, glon))
		del data

		# Update month
		print monst, moned
		monst = monst + relativedelta(months=1)

	# stacking
	data_mon = vstack(data_mon)
	# data_mon = vstack(data_mon)
	if not os.path.exists('%s%s' % (workspace, var)):
		os.makedirs('%s%s' % (workspace, var))
	data_mon.dump('%s%s/%s_monthly_%s-%s' %(workspace, varname[i], varname[i], styr, edyr))
	del data_mon

exit()
# for i in xrange(0, len(forcing)):
# 	data = load('%s%s/%s_monthly_%s-%s' %(workspace, varname[i], varname[i], styr, edyr))
# 	for lon in xrange(0, glon):
# 		for lat in xrange(0, glat):
# 			# 1st: use detrend in mlab
# 			data_detrend = mlab.detrend_linear(timeseries)
# 			ave = np.mean(timeseries)
# 			timeseries_update = data_detrend + ave
# 			timeseries_update.dump('%s%s/pgf_%s_detrend_%s-%s' %(workspace, var, var, lat, lon))
# 			del timeseries_update, timeseries, data_detrend
		# 	    y = np.asarray(y)
	#
    # if y.ndim > 1:
    #     raise ValueError('y cannot have ndim > 1')
	#
    # # short-circuit 0-D array.
    # if not y.ndim:
    #     return np.array(0., dtype=y.dtype)
	#
    # x = np.arange(y.size, dtype=np.float_)
	#
    # C = np.cov(x, y, bias=1)
    # b = C[0, 1]/C[0, 0]
	#
    # a = y.mean() - b*x.mean()
    # return y - (b*x + a)
# curday = stdy
# while curday <= datetime.date(edyr, 12, 31):
# 	last_month = 1
# 	data_mon = []
#
#
# 	# if last_month is not curday.month:
# 	# 	last_month = curday.month
# 	for var in forcing:
# 		file_in = '%s%s/%s.%4d%02d%02d.nc' % (datadir, curday.year, var, curday.year, curday.month, curday.day)
# 		file_out = '%s%s/%s.detrend.%4d%02d%02d.nc' % (workspace, curday.year, var, curday.year, curday.month, curday.day)
# 		data_mon.append(Dataset(file_in).variables[var][:].reshape(1, glat, glon))
# 		data_mon = vstack(data_mon)

	# 					timeseries.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(glat, glon)[lat, lon])
	# # Create the output file
	# file_out = '%s'
	# vars = var
	# nt = 1
	# tstep = 'years'
	# fp = IO.Create_NETCDF_File(dims, file_out, var, varname, datetime.datetime(iyear, 1, 1), tstep, nt)

	# ts = Series(data_detrend, index=dates)
	# print ts[dt.datetime(1948, 12, 29):dt.datetime(1949, 1, 4)]
	#		data = load('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))

	# growing season??
