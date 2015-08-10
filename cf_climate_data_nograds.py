#!/usr/bin/env python
__author__ = 'lpeng'

"""Counterfactual climate datasets forcing"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. extract point data time series
# 	2. detrend tas
# 	3. moving window correlation: look at the correlation changes over time
#	4. variables intercorrelation using matrix plot
#	5. variables correlation at different time scales
##============================================================================================

## import library
##---------------
import sys, os, glob, gc
# time handling
import time, calendar
import datetime as dt
from pandas.tseries.offsets import Day
import pandas as pd
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
orgdir = '/home/air2/oldair/raid6/justin/global/forcings/1.0deg/3hourly2daily/'
# orgdir = '/home/raid9/justin/global/forcings/1.0deg/3hourly2daily/'
forcing = ('tas', 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin')
datadir = '/home/water5/lpeng/Data/pgf/'
# # east africa
# maskpath = '/home/water5/lpeng/Masks/1.0deg/regions/mask_region_'
# masklist = ('eaf','ala', 'amz','aus','cam','cas','cna','grl','med','nas','nec','neu','saf','sah','sahel','sas','sea','ssa','tib','waf','wna','eas','ena','world')

styr = 1948
edyr = 2012
# # dates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')
# #
# # read point data
# path = '/home/water5/lpeng/Data/pgf/'
# # tas = fromfile('%stas_%s-%s_point.bin' % (path, str(styr), str(edyr)), 'float32')
# data = fromfile('%sZABE_dlwrf_1948-2012_point.bin' % (path),'float32')
# figure()
# plot(data)
# plt.show()
# exit()

# site = ("ZABL", "ZANE", "ZABE")
# lat = (27, 30, 29)
# lon = (62, 63, 62)


# tas_detrend = mlab.detrend_linear(tas)
# ts = Series(tas_detrend, index=dates)
# print ts[dt.datetime(1948, 12, 29):dt.datetime(1949, 1, 4)]
#
# stdy = datetime.date(1948, 1, 1)
# eddy = datetime.date(2012, 12, 31)
# delta = (eddy - stdy).days
#
# # print stdy.day
# # print (stdy + datetime.timedelta(5))
#
# ## read forcing list 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin'
# data = [Series(fromfile('%s%s_%s-%s_point.bin' % (path, var, str(styr), str(edyr)), 'float32'), index=dates) for var in forcing[1:]]
# # print data[0]["1948-01-01"]
#
# # sampling
# ensemble = np.empty((len(forcing)-1, 365, 10))  # delta
# for d in xrange(0, 365):  # delta):
# 	curdy = stdy + dt.timedelta(d)
# 	# For each single day, sample an ensemble with a 7-day window across multiple years
# 	pool = Series()  # initialize a Series-type variable
# 	if curdy.day == 29 and curdy.month == 2:
# 		for year in xrange(styr+1, styr+10): #edyr+1):
# 			if calendar.isleap(year):
# 				print year
# 				curdy_year = dt.datetime(year, curdy.month, curdy.day)
# 				pool = pool.append(ts[curdy_year-3*Day(): curdy_year+3*Day()])
# 	else:
# 		for year in xrange(styr+1, styr+10): #edyr+1):
# 			curdy_year = dt.datetime(year, curdy.month, curdy.day)
# 			pool = pool.append(ts[curdy_year-3*Day(): curdy_year+3*Day()])
#
# 	# Pick up the first 10 days with closest values
# 	dif = abs(pool - ts[curdy])
# 	# sort by values
# 	collect = dif.order()
# 	# constraint
# 	dy_collect = collect[:10].index
#
# 	for j in xrange(0, len(forcing)-1):
# 		# for i in xrange(0, 10):
# 		# 	day = dy_collect[i]
# 		# print dy_collect
# 		# print data[j][dy_collect]
# 		# print year, curdy.month, curdy.day
# 		ensemble[j,d,:] = data[j][dy_collect]
#
# # print ensemble[2,:,:]
# figure()
# plot(ensemble[1,:,1])
# plot(data[1][:356])
# # plot(ensemble[7,:,0])
# plt.show()
#
# exit()
#
# # for day in xrange(0, len(tas)):
#
#
# figure()
# plot(tas)
# plot(tas_detrend)
# plt.show()
# exit()


# extract data
#--------------
# get the lon, lat specific time series for all the climate variables
# South Africa
# (ZABL: 28.940S, 26.11E) (ZANE: 27.85S, 29.85E)  (ZABE: 28.33S, 28.170E)
# site = ("ZABL", "ZANE", "ZABE")
# lon = (27, 30, 29)
# lat = (62, 63, 62)

# (dtcm: 19.010N, 99.01E) (FLSC:34.0N,-100.0E)
site = ("DTCM", "FLSC")
lon = (100, 261)
lat = (110, 125)

for i in xrange(0, 2):
	for var in forcing:
		tic = time.clock()
		data = [fromfile('%s%s/%s_%s-%s.bin' % (orgdir, var, var, str(year), str(year)), 'float32').reshape(-1, 180, 360)[:, lat[i], lon[i]] for year in xrange(styr, edyr+1)]
		ts = np.hstack(data)		# data = np.concatenate((data, ts))  # np.append(data, ts)
		ts.astype('float32').tofile('%s%s_%s_%s-%s_point.bin' % (datadir, site[i], var, str(styr), str(edyr)))
		del ts
		del data
		toc = time.clock()
		print toc - tic
exit()


#----Old Code
# Beware of the leap year
# doyave = ts.groupby([ts.index.month, ts.index.day]).mean()
# a=ts[ts.index==datetime(1949,1,1)]
# print a
# print doyave
# print doyave.index[1][0]
# doyave = ts.groupby(ts.index.dayofyear).mean()  # just for single year, without consideration of leap year
# out = ts[ts.index.map(lambda x: x[0] in doyave.index.month)]
# ts - doyave if ts.index.month
# df = DataFrame()
# df['absolute'] = ts
	# # ts = ts.groupby(ts.index.dayofyear)
	# # dfts = df.set_index('data_time')
	# ts = ts.groupby([lambda x:x.month, lambda x:x.day])
	# print ts
	# clim = DataFrame(ave, columns=['climatology'])
	# # print clim
	# df = df.join(clim, on='doy', how='left')
	# anomaly = ts['absolute'] - df['climatology']
	# print anomaly
	# print dayave
	# print dayave1
		# print data  # file.mean(0)[::-1]

